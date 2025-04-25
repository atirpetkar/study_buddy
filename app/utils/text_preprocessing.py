# app/utils/text_preprocessing.py
import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """
    Clean and normalize text for better chunking
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Normalize line endings
    text = re.sub(r'\r\n', '\n', text)
    
    # Remove excessive whitespace
    text = re.sub(r' {2,}', ' ', text)
    
    # Normalize multiple newlines (keep at most 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Ensure sections and headings are properly spaced
    text = re.sub(r'(#+)\s*(.+?)\s*\n', r'\n\1 \2\n\n', text)
    
    # Ensure lists are properly formatted
    text = re.sub(r'\n(\s*[-*•]\s*)', r'\n\1', text)
    
    return text.strip()

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using regex
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Pattern to match sentence boundaries
    pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+(?=[A-Z]|\d+\.)(?!e\.g\.|i\.e\.|etc\.)'
    
    # Split by the pattern
    sentences = re.split(pattern, text)
    
    # Further process to handle list items and other special cases
    result = []
    for sentence in sentences:
        # Trim whitespace
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Handle list items
        list_items = re.split(r'\n\s*[-*•]\s+', sentence)
        if len(list_items) > 1:
            result.append(list_items[0])
            for item in list_items[1:]:
                if item.strip():
                    result.append(f"- {item.strip()}")
        else:
            result.append(sentence)
    
    return result

def chunk_by_paragraphs(text: str, max_chunk_size: int = 1200, overlap: int = 150) -> List[str]:
    """
    Create chunks based on paragraph boundaries
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap
        
    Returns:
        List of text chunks
    """
    # Split text into paragraphs (defined by double newline)
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # If adding this paragraph would exceed the max size and we already have content
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            # Add current chunk to results
            chunks.append(current_chunk.strip())
            
            # Create overlap for next chunk
            # Find the last sentence break in the last ~150 chars if possible
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            
            # Start next chunk with the overlap
            current_chunk = overlap_text
        
        # Add paragraph to current chunk
        if current_chunk and not current_chunk.endswith("\n"):
            current_chunk += "\n\n"
        
        current_chunk += paragraph
    
    # Add the last chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def chunk_by_sections(text: str, max_chunk_size: int = 1200) -> List[str]:
    """
    Chunk text by maintaining section integrity
    
    Args:
        text: Text to chunk
        max_chunk_size: Target maximum size for each chunk
        
    Returns:
        List of text chunks
    """
    # Identify sections (headings)
    section_pattern = r'(^|\n)(#+)\s+(.+?)(?=\n)'
    sections = []
    last_end = 0
    
    for match in re.finditer(section_pattern, text):
        if last_end > 0:  # Not the first section
            section_text = text[last_end:match.start()]
            if section_text.strip():
                sections.append(section_text)
        
        last_end = match.start()
    
    # Add the last section
    if last_end < len(text):
        section_text = text[last_end:]
        if section_text.strip():
            sections.append(section_text)
    
    # If no sections were found, fall back to paragraph chunking
    if not sections:
        return chunk_by_paragraphs(text, max_chunk_size)
    
    # Process each section
    chunks = []
    current_chunk = ""
    
    for section in sections:
        # If the section itself is too large, split it by paragraphs
        if len(section) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            # Split this large section into paragraph chunks
            section_chunks = chunk_by_paragraphs(section, max_chunk_size)
            chunks.extend(section_chunks)
        else:
            # If adding this section would exceed chunk size and we have content
            if len(current_chunk) + len(section) > max_chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            # Add section to current chunk
            if current_chunk and not current_chunk.endswith("\n"):
                current_chunk += "\n\n"
            
            current_chunk += section
    
    # Add the final chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def smart_chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> List[str]:
    """
    Intelligently chunk text by maintaining semantic structure
    
    Args:
        text: Text to chunk
        chunk_size: Target size for each chunk
        overlap: Amount of overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Clean the text first
    text = clean_text(text)
    
    # Check if this looks like a markdown document with sections
    if re.search(r'#+\s+.+', text):
        chunks = chunk_by_sections(text, chunk_size)
    else:
        # Otherwise, chunk by paragraphs
        chunks = chunk_by_paragraphs(text, chunk_size, overlap)
    
    # Post-process chunks to ensure they don't end or start awkwardly
    processed_chunks = []
    
    for chunk in chunks:
        # Don't include empty chunks
        if not chunk.strip():
            continue
        
        # Make sure chunks don't start or end with isolated list markers
        chunk = re.sub(r'^\s*[-*•]\s*$', '', chunk)
        chunk = re.sub(r'\n\s*[-*•]\s*$', '', chunk)
        
        # Ensure chunk doesn't end in the middle of a heading
        if re.search(r'#+\s*$', chunk):
            next_newline = chunk.rstrip().rfind('\n')
            if next_newline > 0:
                # Cut the chunk at the last complete line
                chunk = chunk[:next_newline].rstrip()
        
        # Add to processed chunks if not empty
        if chunk.strip():
            processed_chunks.append(chunk.strip())
    
    return processed_chunks