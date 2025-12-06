import os
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
import pdfplumber
from .base_loader import BaseLoader

class PDFLoader(BaseLoader):
    """Load PDF files"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pdf_config = config.get('pdf', {})
        self.directory = self.pdf_config.get('directory', './data/pdfs')
        self.recursive = self.pdf_config.get('recursive', True)
    
    def load(self) -> List[Dict[str, Any]]:
        if not self.is_enabled():
            return []
        
        pdf_dir = Path(self.directory)
        if not pdf_dir.exists():
            print(f"⚠️  PDF directory not found: {self.directory}")
            return []
        
        documents = []
        pattern = "**/*.pdf" if self.recursive else "*.pdf"
        
        for pdf_file in pdf_dir.glob(pattern):
            try:
                # Try pdfplumber first (better text extraction)
                try:
                    with pdfplumber.open(pdf_file) as pdf:
                        text_parts = []
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                text_parts.append(text)
                        content = "\n\n".join(text_parts)
                except:
                    # Fallback to PyPDF2
                    with open(pdf_file, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        text_parts = []
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text:
                                text_parts.append(text)
                        content = "\n\n".join(text_parts)
                
                if content.strip():
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': 'pdf',
                            'file_path': str(pdf_file),
                            'file_name': pdf_file.name
                        }
                    })
            except Exception as e:
                print(f"⚠️  Error loading PDF {pdf_file}: {str(e)}")
                continue
        
        print(f"✅ Loaded {len(documents)} PDF files")
        return documents

