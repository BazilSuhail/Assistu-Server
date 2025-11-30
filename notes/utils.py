import fitz  # PyMuPDF
import json
import requests
from django.conf import settings
from .models import Note
from datetime import datetime

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        file_content = pdf_file.read()
        from io import BytesIO
        pdf_stream = BytesIO(file_content)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text() + "\n"
        
        doc.close()
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def chunk_text(text, chunk_size=1000):
    """Split text into chunks separated by sentences"""
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def generate_summary_with_llm(text_chunks):
    """Generate summary from text chunks using LLM"""
    llm_url = getattr(settings, "GROQ_LLM_URL", "https://api.groq.com/openai/v1/chat/completions").strip()  # Removed extra spaces
    api_key = settings.GROQ_API_KEY
    
    if not api_key:
        raise Exception("GROQ_API_KEY is not set in settings")
    
    full_text = " ".join(text_chunks[:3]) if len(text_chunks) > 3 else " ".join(text_chunks)
    
    # Limit text length
    if len(full_text) > 3000:
        full_text = full_text[:3000]
    
    prompt = f"""
    Summarize this text in 2-3 sentences and provide key explanations as bullet points. Return ONLY this JSON format:
    {{
        "summary": "summary text",
        "explanation": ["bullet point 1", "bullet point 2", "bullet point 3"]
    }}
    
    Text: {full_text}
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that returns only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(llm_url, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        
        data = res.json()
        
        if "choices" not in data or len(data["choices"]) == 0:
            raise Exception("No choices in response")
        
        content = data["choices"][0]["message"]["content"].strip()
        
        # Clean response
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        return result.get('summary', ''), result.get('explanation', [])
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON response: {content}")
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}")

def generate_tags_with_llm(summary):
    """Generate tags from summary using LLM"""
    llm_url = getattr(settings, "GROQ_LLM_URL", "https://api.groq.com/openai/v1/chat/completions").strip()  # Removed extra spaces
    api_key = settings.GROQ_API_KEY
    
    if not api_key:
        raise Exception("GROQ_API_KEY is not set in settings")
    
    if len(summary) > 1000:
        summary = summary[:1000]
    
    prompt = f"""
    From this summary: {summary}
    Return ONLY this JSON format:
    {{
        "tags": ["tag1", "tag2"],
        "categories": ["cat1"],
        "keywords": ["keyword1", "keyword2"],
        "importance": "low|medium|high"
    }}
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that returns only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(llm_url, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        
        data = res.json()
        
        if "choices" not in data or len(data["choices"]) == 0:
            raise Exception("No choices in response")
        
        content = data["choices"][0]["message"]["content"].strip()
        
        # Clean response
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        return {
            'tags': result.get('tags', []),
            'categories': result.get('categories', ['General']),
            'keywords': result.get('keywords', []),
            'importance': result.get('importance', 'medium')
        }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON response: {content}")
    except Exception as e:
        raise Exception(f"Error generating tags: {str(e)}")


def process_pdf_note(user, pdf_file, title, subject):
    """Process PDF file and create a Note"""
    pdf_text = extract_text_from_pdf(pdf_file)
    
    if not pdf_text.strip():
        raise ValueError("PDF contains no readable text")
    
    text_chunks = chunk_text(pdf_text)
    transcript = ", ".join(text_chunks)
    
    summary, explanation = generate_summary_with_llm(text_chunks)
    metadata = generate_tags_with_llm(summary)
    
    note = Note(
        user=user,
        title=title,
        transcript=transcript,
        summary=summary,
        explanation=explanation,
        subject=subject,
        categories=metadata['categories'],
        keywords=metadata['keywords'],
        importance=metadata['importance'],
        tags=metadata['tags']
    )
    
    note.save()
    return note

def create_note_from_text(user, title, text, subject):
    """Create a note from provided text"""
    if not text.strip():
        raise ValueError("Text content cannot be empty")
    
    text_chunks = chunk_text(text)
    transcript = ", ".join(text_chunks)
    
    summary, explanation = generate_summary_with_llm(text_chunks)
    metadata = generate_tags_with_llm(summary)
    
    note = Note(
        user=user,
        title=title,
        transcript=transcript,
        summary=summary,
        explanation=explanation,
        subject=subject,
        categories=metadata['categories'],
        keywords=metadata['keywords'],
        importance=metadata['importance'],
        tags=metadata['tags']
    )
    
    note.save()
    return note

def create_note_from_text(user, title, text, subject):
    """Create a note from provided text"""
    if not text.strip():
        raise ValueError("Text content cannot be empty")
    
    text_chunks = chunk_text(text)
    transcript = ", ".join(text_chunks)
    
    summary = generate_summary_with_llm(text_chunks)
    metadata = generate_tags_with_llm(summary)
    
    note = Note(
        user=user,
        title=title,
        transcript=transcript,
        summary=summary,
        subject=subject,
        categories=metadata['categories'],
        importance=metadata['importance'],
        tags=metadata['tags']
    )
    
    note.save()
    return note