from sentence_transformers import SentenceTransformer
from typing import List
import torch

class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"📦 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("✅ Embedding model loaded")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()

