# Google Ads RAG System

A complete Retrieval-Augmented Generation (RAG) system for Google Ads API documentation, built with Django, LangChain, and Qdrant.

## 🎯 **Overview**

This RAG system scrapes official Google Ads API documentation, creates embeddings, stores them in a vector database, and provides intelligent question-answering capabilities through Django API endpoints.

## 🏗️ **Architecture**

```
Google Ads Docs → Web Scraper → Text Chunks → Embeddings → Vector DB (Qdrant) → RAG Client → Django API
```

## 📋 **Features**

- ✅ **Web Scraping**: Automatically scrapes 43 Google Ads API documentation URLs
- ✅ **Text Chunking**: Intelligent text splitting with configurable chunk size and overlap
- ✅ **Embeddings**: Uses OpenAI's text-embedding-3-large model
- ✅ **Vector Storage**: Qdrant vector database for similarity search
- ✅ **RAG Pipeline**: LangChain-based question-answering system
- ✅ **Django Integration**: RESTful API endpoints
- ✅ **Authentication**: JWT-based authentication for protected endpoints
- ✅ **Management Commands**: Django management commands for setup

## 🚀 **Quick Start**

### **1. Install Dependencies**

```bash
pip install -r google_ads_new/requirements_rag.txt
```

### **2. Set Environment Variables**

```bash
export OPENAI_API_KEY="your_openai_api_key"
export QDRANT_URL="http://localhost:6333"  # Optional, defaults to localhost
```

### **3. Start Qdrant (Vector Database)**

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or using Qdrant binary
# Download from https://qdrant.tech/documentation/quick-start/
```

### **4. Set Up RAG System**

```bash
# Scrape docs and create embeddings
python manage.py setup_rag

# Or with custom options
python manage.py setup_rag --recreate --chunk-size 800 --chunk-overlap 200
```

### **5. Test the System**

```bash
# Run the test script
python google_ads_new/test_rag_system.py

# Or test individual components
python manage.py shell
>>> from google_ads_new.rag_client import get_rag_client
>>> rag = get_rag_client()
>>> result = rag.query("How do I get started with Google Ads API?")
>>> print(result['answer'])
```

## 🔧 **API Endpoints**

### **Basic Endpoints (No Authentication)**

#### **Query RAG System**
```http
POST /google-ads-new/api/rag/query/
Content-Type: application/json

{
  "query": "How do I authenticate with Google Ads API?"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "To authenticate with Google Ads API, you need to...",
  "sources": [
    {
      "source": "https://developers.google.com/google-ads/api/docs/oauth/overview",
      "chunk": 0,
      "section": "oauth",
      "text_preview": "OAuth 2.0 is the authentication protocol used by Google Ads API..."
    }
  ],
  "query": "How do I authenticate with Google Ads API?"
}
```

#### **Search Documents**
```http
POST /google-ads-new/api/rag/search/
Content-Type: application/json

{
  "query": "OAuth setup",
  "limit": 5
}
```

#### **Get System Status**
```http
GET /google-ads-new/api/rag/status/
```

#### **Rebuild Vector Store**
```http
POST /google-ads-new/api/rag/rebuild/
```

### **REST API Endpoints (Authentication Required)**

#### **Authenticated Query**
```http
POST /google-ads-new/api/rag/api/query/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "query": "How do I create a campaign?"
}
```

## 🧪 **Testing**

### **Test Script**
```bash
python google_ads_new/test_rag_system.py
```

### **cURL Examples**

```bash
# Query the RAG system
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "How do I get started with Google Ads API?"}'

# Search documents
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/search/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "OAuth setup", "limit": 5}'

# Get status
curl -X GET 'http://localhost:8000/google-ads-new/api/rag/status/'
```

## 📊 **Configuration**

### **Chunking Parameters**
- **chunk_size**: 800-1500 characters (default: 1000)
- **chunk_overlap**: 100-300 characters (default: 200)

### **Embedding Model**
- **Model**: text-embedding-3-large
- **Dimensions**: 3072
- **Distance**: Cosine similarity

### **Retrieval Parameters**
- **k**: Number of similar documents to retrieve (default: 4)
- **score_threshold**: Minimum similarity score (default: 0.7)

## 🔍 **Usage Examples**

### **Python Integration**

```python
from google_ads_new.rag_client import get_rag_client

# Get RAG client
rag_client = get_rag_client()

# Query the system
result = rag_client.query("How do I create a campaign?")
print(result['answer'])

# Search for similar documents
docs = rag_client.get_similar_docs("OAuth setup", limit=5)
for doc in docs:
    print(f"Source: {doc['source']}")
    print(f"Text: {doc['text'][:200]}...")
```

### **Django View Integration**

```python
from django.http import JsonResponse
from google_ads_new.rag_client import get_rag_client

def my_view(request):
    query = request.GET.get('q', '')
    rag_client = get_rag_client()
    result = rag_client.query(query)
    return JsonResponse(result)
```

## 📁 **File Structure**

```
google_ads_new/
├── document_scraper.py          # Web scraping logic
├── vector_store.py              # Vector database operations
├── rag_client.py                # RAG client and LangChain integration
├── rag_views.py                 # Django API views
├── constants.py                 # Documentation URLs
├── management/
│   └── commands/
│       └── setup_rag.py         # Django management command
├── test_rag_system.py           # Test script
├── requirements_rag.txt         # RAG dependencies
└── RAG_SYSTEM_README.md         # This file
```

## 🛠️ **Management Commands**

### **Setup RAG System**
```bash
python manage.py setup_rag [options]

Options:
  --recreate              Recreate the vector store collection
  --chunk-size SIZE       Size of text chunks (default: 1000)
  --chunk-overlap SIZE    Overlap between chunks (default: 200)
  --collection-name NAME  Name of the collection (default: google_ads_docs)
```

### **Example Usage**
```bash
# Basic setup
python manage.py setup_rag

# Recreate with custom parameters
python manage.py setup_rag --recreate --chunk-size 800 --chunk-overlap 200

# Custom collection name
python manage.py setup_rag --collection-name my_ads_docs
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Qdrant Connection Error**
   ```bash
   # Make sure Qdrant is running
   docker run -p 6333:6333 qdrant/qdrant
   ```

2. **OpenAI API Key Error**
   ```bash
   # Set your OpenAI API key
   export OPENAI_API_KEY="your_key_here"
   ```

3. **Memory Issues with Large Documents**
   ```bash
   # Reduce chunk size
   python manage.py setup_rag --chunk-size 500 --chunk-overlap 100
   ```

4. **Scraping Errors**
   ```bash
   # Check internet connection and try again
   python manage.py setup_rag --recreate
   ```

### **Logging**

Enable detailed logging by setting the log level:

```python
# In Django settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'google_ads_new': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📈 **Performance Optimization**

### **Chunking Strategy**
- **Small chunks (500-800)**: Better precision, more chunks
- **Large chunks (1000-1500)**: Better context, fewer chunks
- **Overlap (100-300)**: Maintains context across boundaries

### **Retrieval Optimization**
- **k=4**: Good balance of context and performance
- **score_threshold=0.7**: Filters out irrelevant results
- **Batch processing**: Processes documents in batches

### **Caching**
- **RAG client**: Singleton pattern for connection reuse
- **Embeddings**: Cached by LangChain
- **Vector store**: Qdrant handles caching internally

## 🔒 **Security Considerations**

1. **API Keys**: Store OpenAI API key securely
2. **Authentication**: Use JWT tokens for protected endpoints
3. **Rate Limiting**: Implement rate limiting for production
4. **Input Validation**: Validate all user inputs
5. **Error Handling**: Don't expose sensitive information in errors

## 🚀 **Production Deployment**

### **Environment Variables**
```bash
export OPENAI_API_KEY="your_production_key"
export QDRANT_URL="https://your-qdrant-cluster.com"
export DJANGO_SECRET_KEY="your_secret_key"
```

### **Docker Compose Example**
```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
  
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - qdrant
```

## 📝 **Notes**

- **Documentation URLs**: 43 official Google Ads API documentation URLs
- **Text Processing**: Removes navigation, scripts, and styling
- **Metadata**: Includes source URL, chunk index, and section
- **Error Handling**: Graceful handling of scraping and API errors
- **Scalability**: Designed to handle large document collections

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is part of the marketing assistant backend system.
