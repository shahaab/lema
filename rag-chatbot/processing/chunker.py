from typing import List, Dict, Any
import re

class Chunker:
    """Split documents into chunks"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split a document into chunks"""
        # Simple sentence-based chunking
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'content': chunk_text,
                    'metadata': {**metadata, 'chunk_index': len(chunks)}
                })
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-self._get_overlap_sentence_count():]
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'content': chunk_text,
                'metadata': {**metadata, 'chunk_index': len(chunks)}
            })
        
        return chunks
    
    def _get_overlap_sentence_count(self) -> int:
        """Calculate number of sentences for overlap"""
        # Rough estimate: overlap / average sentence length
        return max(1, self.chunk_overlap // 20)

