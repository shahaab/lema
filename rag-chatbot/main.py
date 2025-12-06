import yaml
import os
from dotenv import load_dotenv
from pathlib import Path

from data_ingestion import EmailLoader, JiraLoader, PDFLoader, DocumentLoader
from processing import Chunker, EmbeddingGenerator
from storage import VectorDB

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_enabled_loaders(config):
    """Get list of enabled data loaders"""
    loaders = []
    data_sources = config.get('data_sources', {})
    
    if data_sources.get('email', {}).get('enabled', False):
        email_config = {
            'enabled': True,
            'collection_name': data_sources['email']['collection_name'],
            'email': config.get('email', {})
        }
        loaders.append(EmailLoader(email_config))
    
    if data_sources.get('jira', {}).get('enabled', False):
        jira_config = {
            'enabled': True,
            'collection_name': data_sources['jira']['collection_name'],
            'jira': config.get('jira', {})
        }
        loaders.append(JiraLoader(jira_config))
    
    if data_sources.get('pdf', {}).get('enabled', False):
        pdf_config = {
            'enabled': True,
            'collection_name': data_sources['pdf']['collection_name'],
            'pdf': config.get('pdf', {})
        }
        loaders.append(PDFLoader(pdf_config))
    
    if data_sources.get('document', {}).get('enabled', False):
        doc_config = {
            'enabled': True,
            'collection_name': data_sources['document']['collection_name'],
            'document': config.get('document', {})
        }
        loaders.append(DocumentLoader(doc_config))
    
    return loaders

def main():
    """Main function to load data and build vector database"""
    # Load environment variables
    load_dotenv()
    
    # Load configuration
    config = load_config()
    
    # Get enabled loaders
    loaders = get_enabled_loaders(config)
    
    if not loaders:
        print("⚠️  No data sources enabled! Please enable at least one in config.yaml")
        return
    
    print(f"📚 Loading data from {len(loaders)} source(s)...\n")
    
    # Load all documents
    all_documents = []
    for loader in loaders:
        documents = loader.load()
        all_documents.extend(documents)
    
    if not all_documents:
        print("⚠️  No documents loaded!")
        return
    
    print(f"\n📄 Total documents loaded: {len(all_documents)}\n")
    
    # Process documents
    processing_config = config.get('processing', {})
    chunker = Chunker(
        chunk_size=processing_config.get('chunk_size', 512),
        chunk_overlap=processing_config.get('chunk_overlap', 50)
    )
    
    print("✂️  Chunking documents...")
    all_chunks = []
    for doc in all_documents:
        chunks = chunker.chunk_document(doc['content'], doc['metadata'])
        all_chunks.extend(chunks)
    
    print(f"✅ Created {len(all_chunks)} chunks\n")
    
    # Generate embeddings
    embedding_model = processing_config.get('embedding_model', 'all-MiniLM-L6-v2')
    embedding_generator = EmbeddingGenerator(embedding_model)
    
    print("🔢 Generating embeddings...")
    texts = [chunk['content'] for chunk in all_chunks]
    embeddings = embedding_generator.generate_embeddings(texts)
    print("✅ Embeddings generated\n")
    
    # Store in vector DB
    vector_db_config = config.get('vector_db', {})
    vector_db = VectorDB(
        persist_directory=vector_db_config.get('persist_directory', './chroma_db'),
        collection_name=vector_db_config.get('collection_name', 'rag_collection')
    )
    
    print("💾 Storing in vector database...")
    vector_db.add_documents(all_chunks, embeddings)
    
    # Print stats
    stats = vector_db.get_collection_stats()
    print(f"\n✅ Done! Vector DB contains {stats['total_documents']} documents")

if __name__ == "__main__":
    main()

