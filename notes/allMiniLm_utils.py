import onnxruntime as ort
from transformers import AutoTokenizer
import numpy as np
from django.conf import settings
import os

# Initialize ONNX model and tokenizer (load once at module level)
MODEL_DIR = os.path.join(settings.BASE_DIR, "all-MiniLM-L6-v2")
session = ort.InferenceSession(
    f"{MODEL_DIR}/model.onnx", 
    providers=["CPUExecutionProvider"]
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

def embed_texts(texts):
    """
    Generate embeddings for a list of texts using ONNX model
    """
    if not texts:
        return np.array([])
    
    # Tokenize → return numpy instead of torch
    inputs = tokenizer(
        texts, 
        return_tensors="np", 
        padding=True, 
        truncation=True,
        max_length=512
    )

    # ONNX forward pass
    outputs = session.run(None, dict(inputs))

    # Mean pooling (last_hidden_state)
    last_hidden = outputs[0]  # shape (batch, seq, hidden)
    mask = inputs["attention_mask"][:, :, None]
    mean_pooled = (last_hidden * mask).sum(1) / mask.sum(1)

    # Normalize
    norms = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
    embeddings = mean_pooled / norms
    return embeddings

def calculate_cosine_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two embeddings
    """
    return np.dot(embedding1, embedding2)

def search_similar_notes(user, query_text, similarity_threshold=0.2):
    """
    Search for notes with similar content based on semantic similarity
    Returns ALL notes with relevance scores scaled to 100%
    
    Args:
        user: User object
        query_text: Search query string
        similarity_threshold: Not used anymore (kept for backward compatibility)
    
    Returns:
        List of ALL notes with similarity scores (0-100%), sorted by relevance
    """
    from .models import Note
    
    # Get all notes for the user
    notes = Note.objects(user=user)
    
    if not notes:
        return []
    
    # Generate query embedding
    query_embedding = embed_texts([query_text])[0] 
    
    # Collect all summaries and note data
    summaries = []
    note_data = []
    
    for note in notes:
        if note.summary:  # Only include notes with summaries
            summaries.append(note.summary)
            note_data.append(note)
    
    if not summaries:
        return []
    
    # Generate embeddings for all summaries
    summary_embeddings = embed_texts(summaries)
    
    # Calculate similarities for ALL notes and scale to 100%
    results = []
    for i, note in enumerate(note_data):
        similarity = calculate_cosine_similarity(query_embedding, summary_embeddings[i])
        
        # Scale similarity to percentage (0-100%)
        # Cosine similarity ranges from -1 to 1, but typically 0 to 1 for normalized embeddings
        # We scale it to 0-100%
        relevance_score = float(similarity * 100)
        
        results.append({
            'note': note,
            'similarity': relevance_score  # Now scaled to 0-100%
        })
    
    # Sort by similarity (highest first)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return results