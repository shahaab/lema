import requests
import json
from typing import List, Dict, Any

class Generator:
    """Generate answers using Ollama LLM"""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434", 
                 temperature: float = 0.7, max_tokens: int = 512):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate answer from query and context"""
        # Build context string
        context_text = "\n\n".join([
            f"[Document {i+1}]:\n{doc['content']}" 
            for i, doc in enumerate(context)
        ])
        
        # Build prompt
        prompt = f"""Use the following context to answer the question. If the answer is not in the context, say so.

Context:
{context_text}

Question: {query}

Answer:"""
        
        # Call Ollama API
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get('response', 'Sorry, I could not generate an answer.')
        except requests.exceptions.RequestException as e:
            return f"Error calling LLM: {str(e)}. Make sure Ollama is running and the model is installed."

