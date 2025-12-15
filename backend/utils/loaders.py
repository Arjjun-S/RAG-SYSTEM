"""
Text file loaders for PDF and TXT documents.
Lightweight implementations suitable for free tier deployment.
"""
import io
from typing import Tuple


def load_txt(content: bytes, filename: str) -> Tuple[str, dict]:
    """
    Load text from a TXT file.
    
    Args:
        content: Raw file bytes
        filename: Original filename
        
    Returns:
        Tuple of (extracted_text, metadata)
    """
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        # Try common fallback encodings
        try:
            text = content.decode('latin-1')
        except:
            text = content.decode('utf-8', errors='ignore')
    
    metadata = {
        "filename": filename,
        "type": "txt",
        "size": len(content)
    }
    
    return text.strip(), metadata


def load_pdf(content: bytes, filename: str) -> Tuple[str, dict]:
    """
    Load text from a PDF file using PyMuPDF (fitz).
    
    Args:
        content: Raw file bytes
        filename: Original filename
        
    Returns:
        Tuple of (extracted_text, metadata)
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF (fitz) is required for PDF processing. Install with: pip install pymupdf")
    
    text_parts = []
    
    # Open PDF from bytes
    pdf_stream = io.BytesIO(content)
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    
    num_pages = len(doc)
    
    for page_num in range(num_pages):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            text_parts.append(text)
    
    doc.close()
    
    full_text = "\n\n".join(text_parts)
    
    metadata = {
        "filename": filename,
        "type": "pdf",
        "size": len(content),
        "pages": num_pages
    }
    
    return full_text.strip(), metadata


def load_document(content: bytes, filename: str) -> Tuple[str, dict]:
    """
    Load a document based on its file extension.
    
    Args:
        content: Raw file bytes
        filename: Original filename
        
    Returns:
        Tuple of (extracted_text, metadata)
        
    Raises:
        ValueError: If file type is not supported
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.txt'):
        return load_txt(content, filename)
    elif filename_lower.endswith('.pdf'):
        return load_pdf(content, filename)
    else:
        raise ValueError(f"Unsupported file type: {filename}. Only .txt and .pdf are supported.")
