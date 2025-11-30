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
    
    Args:
        user: User object
        query_text: Search query string
        similarity_threshold: Minimum similarity score (default 0.2 = 20%)
    
    Returns:
        List of notes with similarity scores
    """
    from .models import Note
    
    # Get all notes for the user
    notes = Note.objects(user=user)
    
    if not notes:
        return []
    
    # Generate query embedding
    query_embedding = embed_texts([query_text])[0] 
    #print(notes)
    #print(query_text)
    #print(query_embedding)
    
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
    
    # Calculate similarities and filter results
    results = []
    for i, note in enumerate(note_data):
        similarity = calculate_cosine_similarity(query_embedding, summary_embeddings[i])
        
        if similarity >= similarity_threshold:
            results.append({
                'note': note,
                'similarity': float(similarity)
            })
    
    # Sort by similarity (highest first)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return results