# RAG Chatbot - Local & Open Source

A fully local, open-source RAG (Retrieval-Augmented Generation) chatbot that can ingest data from emails, Jira tickets, PDFs, and documents.

## Features

- ✅ **Fully Local**: No external APIs, everything runs on your machine
- ✅ **Toggleable Data Sources**: Enable/disable email, Jira, PDFs, or documents independently
- ✅ **Modular Architecture**: Easy to extend with new data sources
- ✅ **Incremental Updates**: Script to update email data regularly
- ✅ **Free & Open Source**: Uses Ollama, sentence-transformers, and ChromaDB

## Tech Stack

- **LLM**: Ollama (local models like Llama 3.2, Mistral)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB**: ChromaDB
- **Data Sources**: IMAP (email), Jira API, PDFs, Documents

## Setup

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download LLM Model

```bash
ollama pull llama3.2
# Or: ollama pull mistral
```

### 4. Configure

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials (only for enabled sources):
   ```env
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   ```

3. Edit `config.yaml` to enable desired data sources:
   ```yaml
   data_sources:
     email:
       enabled: true  # Change to true
     jira:
       enabled: false
     pdf:
       enabled: true  # Change to true
     document:
       enabled: false
   ```

4. Create data directories (if using PDFs/documents):
   ```bash
   mkdir -p data/pdfs data/documents
   ```

## Usage

### 1. Load Data

```bash
python main.py
```

This will:
- Load data from all enabled sources
- Chunk documents
- Generate embeddings
- Store in vector database

### 2. Start Chat

```bash
python chat.py
```

### 3. Update Emails (Optional)

Run this script periodically to fetch latest emails:

```bash
python scripts/update_data.py
```

You can schedule it with cron:
```bash
# Add to crontab (runs every hour)
0 * * * * cd /path/to/rag-chatbot && python scripts/update_data.py
```

## Configuration

### Data Source Toggles

In `config.yaml`, you can enable/disable each source independently:

```yaml
data_sources:
  email:
    enabled: true  # Toggle email loading
  jira:
    enabled: false  # Toggle Jira loading
  pdf:
    enabled: true   # Toggle PDF loading
  document:
    enabled: false  # Toggle document loading
```

### Email Configuration

For Gmail, you'll need an App Password:
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Generate App Password
4. Use it in `.env` as `EMAIL_PASSWORD`

### Jira Configuration

1. Go to Jira → Account Settings → Security → API Tokens
2. Create API token
3. Use your email and token in `.env`

## Project Structure

```
rag-chatbot/
├── config.yaml              # Main configuration
├── .env                     # Credentials (not in git)
├── main.py                  # Data loading script
├── chat.py                  # Chat interface
├── data_ingestion/          # Data loaders (modular)
│   ├── base_loader.py
│   ├── email_loader.py
│   ├── jira_loader.py
│   ├── pdf_loader.py
│   └── document_loader.py
├── processing/              # Chunking & embeddings
│   ├── chunker.py
│   └── embeddings.py
├── storage/                 # Vector database
│   └── vector_db.py
├── rag/                     # RAG pipeline
│   ├── retriever.py
│   └── generator.py
└── scripts/                 # Utility scripts
    └── update_data.py
```

## Troubleshooting

### Ollama not running
```bash
# Start Ollama
ollama serve

# Or run in background
ollama serve &
```

### Model not found
```bash
# List available models
ollama list

# Pull a model
ollama pull llama3.2
```

### No documents loaded
- Check that at least one data source is enabled in `config.yaml`
- Verify credentials in `.env` (for email/Jira)
- Check that PDF/document directories exist and contain files

## License

MIT

