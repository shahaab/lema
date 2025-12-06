from storage.vector_db import VectorDB
from processing.embeddings import EmbeddingGenerator
from typing import List, Dict, Any

class Retriever:
    """Retrieve relevant documents for a query"""
    
    def __init__(self, vector_db: VectorDB, embedding_generator: EmbeddingGenerator):
        self.vector_db = vector_db
        self.embedding_generator = embedding_generator
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embeddings([query])[0]
        
        # Search vector DB
        results = self.vector_db.search(query_embedding, top_k=top_k)
        
        return results

