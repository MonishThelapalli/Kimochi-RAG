from app.core.logging import logger

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    Simple sliding window chunking based on words/tokens.
    For simplicity, we'll approximate tokens by splitting on whitespace.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        
        # Break if we've reached the end
        if end >= len(words):
            break
            
        start += (chunk_size - overlap)
        
    logger.info("text_chunked", total_chunks=len(chunks))
    return chunks
