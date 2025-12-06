import yaml
from dotenv import load_dotenv
from storage import VectorDB
from processing import EmbeddingGenerator
from rag import Retriever, Generator

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def main():
    """Interactive chat interface"""
    load_dotenv()
    config = load_config()
    
    # Initialize components
    print("🚀 Initializing RAG system...")
    
    vector_db_config = config.get('vector_db', {})
    vector_db = VectorDB(
        persist_directory=vector_db_config.get('persist_directory', './chroma_db'),
        collection_name=vector_db_config.get('collection_name', 'rag_collection')
    )
    
    processing_config = config.get('processing', {})
    embedding_generator = EmbeddingGenerator(
        processing_config.get('embedding_model', 'all-MiniLM-L6-v2')
    )
    
    retriever = Retriever(vector_db, embedding_generator)
    
    llm_config = config.get('llm', {})
    generator = Generator(
        model=llm_config.get('model', 'llama3.2'),
        base_url=llm_config.get('base_url', 'http://localhost:11434'),
        temperature=llm_config.get('temperature', 0.7),
        max_tokens=llm_config.get('max_tokens', 512)
    )
    
    rag_config = config.get('rag', {})
    top_k = rag_config.get('top_k', 5)
    
    # Check if vector DB has data
    stats = vector_db.get_collection_stats()
    if stats['total_documents'] == 0:
        print("⚠️  Vector DB is empty! Run 'python main.py' first to load data.")
        return
    
    print(f"✅ Ready! Vector DB has {stats['total_documents']} documents\n")
    print("💬 Chat with your data (type 'quit' to exit)\n")
    
    while True:
        query = input("You: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
        
        print("\n🔍 Searching...")
        # Retrieve relevant documents
        context = retriever.retrieve(query, top_k=top_k)
        
        if not context:
            print("❌ No relevant documents found.")
            continue
        
        print(f"📚 Found {len(context)} relevant document(s)\n")
        print("🤖 Generating answer...\n")
        
        # Generate answer
        answer = generator.generate(query, context)
        
        print(f"Assistant: {answer}\n")
        print("-" * 80 + "\n")

if __name__ == "__main__":
    main()

