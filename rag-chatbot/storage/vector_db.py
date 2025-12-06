import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os

class VectorDB:
    """ChromaDB wrapper for vector storage"""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "rag_collection"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add documents with embeddings to the collection"""
        if not documents or not embeddings:
            return
        
        ids = [f"{doc['metadata'].get('source', 'unknown')}_{i}" 
               for i, doc in enumerate(documents)]
        texts = [doc['content'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        print(f"✅ Added {len(documents)} documents to vector DB")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
        
        return documents
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': self.collection_name
        }
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ Collection cleared")

