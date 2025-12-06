import os
from pathlib import Path
from typing import List, Dict, Any
from docx import Document
from .base_loader import BaseLoader

class DocumentLoader(BaseLoader):
    """Load Word documents and text files"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.doc_config = config.get('document', {})
        self.directory = self.doc_config.get('directory', './data/documents')
        self.recursive = self.doc_config.get('recursive', True)
        self.extensions = self.doc_config.get('supported_extensions', ['.docx', '.txt'])
    
    def load(self) -> List[Dict[str, Any]]:
        if not self.is_enabled():
            return []
        
        doc_dir = Path(self.directory)
        if not doc_dir.exists():
            print(f"⚠️  Document directory not found: {self.directory}")
            return []
        
        documents = []
        pattern = "**/*" if self.recursive else "*"
        
        for file_path in doc_dir.glob(pattern):
            if file_path.suffix.lower() not in self.extensions:
                continue
            
            try:
                if file_path.suffix.lower() == '.docx':
                    doc = Document(file_path)
                    content = "\n".join([para.text for para in doc.paragraphs])
                elif file_path.suffix.lower() == '.txt':
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                else:
                    continue
                
                if content.strip():
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': 'document',
                            'file_path': str(file_path),
                            'file_name': file_path.name,
                            'file_type': file_path.suffix
                        }
                    })
            except Exception as e:
                print(f"⚠️  Error loading document {file_path}: {str(e)}")
                continue
        
        print(f"✅ Loaded {len(documents)} documents")
        return documents

