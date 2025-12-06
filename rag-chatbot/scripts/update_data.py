import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from dotenv import load_dotenv
from data_ingestion import EmailLoader
from processing import Chunker, EmbeddingGenerator
from storage import VectorDB

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def update_emails():
    """Update email data (incremental)"""
    load_dotenv()
    config = load_config()
    
    # Only update if email is enabled
    if not config.get('data_sources', {}).get('email', {}).get('enabled', False):
        print("⚠️  Email source is not enabled in config.yaml")
        return
    
    print("📧 Updating emails...\n")
    
    # Load new emails
    email_config = {
        'enabled': True,
        'collection_name': config['data_sources']['email']['collection_name'],
        'email': config.get('email', {})
    }
    loader = EmailLoader(email_config)
    documents = loader.load()
    
    if not documents:
        print("No new emails to add.")
        return
    
    # Process and store
    processing_config = config.get('processing', {})
    chunker = Chunker(
        chunk_size=processing_config.get('chunk_size', 512),
        chunk_overlap=processing_config.get('chunk_overlap', 50)
    )
    
    all_chunks = []
    for doc in documents:
        chunks = chunker.chunk_document(doc['content'], doc['metadata'])
        all_chunks.extend(chunks)
    
    embedding_generator = EmbeddingGenerator(
        processing_config.get('embedding_model', 'all-MiniLM-L6-v2')
    )
    
    texts = [chunk['content'] for chunk in all_chunks]
    embeddings = embedding_generator.generate_embeddings(texts)
    
    vector_db_config = config.get('vector_db', {})
    vector_db = VectorDB(
        persist_directory=vector_db_config.get('persist_directory', './chroma_db'),
        collection_name=vector_db_config.get('collection_name', 'rag_collection')
    )
    
    vector_db.add_documents(all_chunks, embeddings)
    print(f"\n✅ Updated! Added {len(all_chunks)} new chunks")

if __name__ == "__main__":
    update_emails()

