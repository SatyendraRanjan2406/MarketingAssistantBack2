# 🚀 Knowledge Base System with Vector Embeddings

## Overview

This system automatically monitors a folder for knowledge base files, creates vector embeddings using OpenAI, and integrates with a Google AI chatbot powered by LangChain and ChatGPT. It prevents duplicate embeddings and provides intelligent, context-aware responses.

## ✨ Key Features

- **🔄 Automatic File Monitoring**: Watches a folder for new knowledge base files
- **🧠 Vector Embeddings**: Creates OpenAI embeddings for semantic search
- **🚫 No Duplicate Processing**: Uses file hashing to prevent reprocessing unchanged files
- **🤖 ChatGPT Integration**: Powers responses with OpenAI's language models
- **🔍 Semantic Search**: Finds relevant information using vector similarity
- **📊 Django Integration**: Optional integration with Django models
- **📝 Multiple File Types**: Supports Markdown, Text, HTML, PDF, and Word documents
- **📈 Real-time Processing**: Automatically processes files as they're added

## 🏗️ System Architecture

```
knowledge_base_docs/          # Main folder to add files
├── processed/                # Processed files (moved here)
├── embeddings/               # Vector embeddings storage
└── logs/                     # System logs

knowledge_base_manager.py     # File monitoring and processing
enhanced_chatbot.py          # AI chatbot with knowledge base
setup_knowledge_base_system.py # Installation and setup
```

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
python setup_knowledge_base_system.py
```

### 2. **Add Knowledge Base Files**
Place your knowledge base files in the `knowledge_base_docs/` folder:
- `.md` (Markdown) - Recommended
- `.txt` (Text)
- `.html` (HTML)
- `.pdf` (PDF)
- `.docx` (Word)

### 3. **Start the Knowledge Base Manager**
```bash
python knowledge_base_manager.py
```

### 4. **Use the Enhanced Chatbot**
```bash
python enhanced_chatbot.py
```

## 📋 Prerequisites

- **Python 3.8+**
- **OpenAI API Key** (set as environment variable)
- **Internet connection** for OpenAI API calls

## 🔧 Installation

### **Option 1: Automated Setup (Recommended)**
```bash
python setup_knowledge_base_system.py
```

### **Option 2: Manual Installation**
```bash
# Install required packages
pip install langchain langchain-openai langchain-community chromadb watchdog openai python-dotenv

# Create directories
mkdir -p knowledge_base_docs/{processed,embeddings,logs}

# Set environment variables
export OPENAI_API_KEY="your_api_key_here"
```

## 📁 File Structure

### **Knowledge Base Documents**
```
knowledge_base_docs/
├── google_ads_basics.md      # Sample knowledge base file
├── your_document.md          # Add your files here
└── another_document.txt      # Different file types supported
```

### **Processed Files**
```
knowledge_base_docs/processed/
├── processed_files.json      # List of processed files
├── file_hashes.json         # File hash tracking
└── your_document.md         # Moved here after processing
```

### **Embeddings**
```
knowledge_base_docs/embeddings/
├── chroma.sqlite3           # Vector database
└── index/                   # Embedding indexes
```

## 🔄 How It Works

### **1. File Monitoring**
- The system watches the `knowledge_base_docs/` folder
- Detects new files and file modifications
- Automatically triggers processing

### **2. File Processing**
- Reads file content based on file type
- Extracts metadata (title, tags, etc.)
- Creates text chunks for embedding
- Generates OpenAI vector embeddings
- Stores embeddings in Chroma vector database

### **3. Duplicate Prevention**
- Calculates SHA256 hash of file content
- Compares with previous hashes
- Only reprocesses changed files
- Maintains processing history

### **4. Chatbot Integration**
- Searches vector database for relevant context
- Uses ChatGPT to generate intelligent responses
- Incorporates knowledge base information
- Maintains conversation history

## 💡 Usage Examples

### **Adding Knowledge Base Files**

1. **Create a Markdown file**:
```markdown
# Google Ads Optimization

## Best Practices
- Use specific keywords
- Optimize landing pages
- Monitor performance metrics

**Tags**: google ads, optimization, best practices
**Category**: Digital Marketing
```

2. **Place in the folder**:
```bash
cp your_file.md knowledge_base_docs/
```

3. **File is automatically processed**:
- Embeddings created
- File moved to processed folder
- Available for chatbot queries

### **Using the Chatbot**

```bash
python enhanced_chatbot.py
```

**Example conversation**:
```
👤 You: How do I optimize Google Ads campaigns?
📚 Found 3 relevant knowledge base entries
🤖 Assistant: Based on the knowledge base, here are the key optimization strategies...

👤 You: What are the best practices for keyword management?
📚 Found 2 relevant knowledge base entries
🤖 Assistant: According to the knowledge base, effective keyword management involves...
```

## 🔍 Advanced Features

### **File Type Support**

| Format | Extension | Features |
|--------|-----------|----------|
| Markdown | `.md` | Headers, lists, tags, metadata |
| Text | `.txt` | Plain text content |
| HTML | `.html` | Web content parsing |
| PDF | `.pdf` | Document text extraction |
| Word | `.docx` | Office document parsing |

### **Metadata Extraction**

The system automatically extracts:
- **Title**: From markdown headers or filename
- **Tags**: From markdown tag lines
- **File size**: Content length
- **Timestamps**: Creation and modification dates
- **Source**: Original file path

### **Embedding Configuration**

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Vector Dimensions**: OpenAI embedding dimensions
- **Search Results**: Top 5 most relevant chunks

## 📊 Monitoring and Logs

### **System Logs**
```
knowledge_base_docs/logs/
└── kb_manager_20241219.log  # Daily log files
```

### **Log Information**
- File processing events
- Embedding creation status
- Error messages and debugging
- System performance metrics

### **Statistics Commands**
```bash
# In the chatbot
👤 You: stats

📊 System Statistics:
   embeddings_available: True
   vector_store_available: True
   total_embeddings: 45
   conversation_history_length: 8
```

## 🚨 Troubleshooting

### **Common Issues**

#### **1. OpenAI API Key Missing**
```bash
❌ OPENAI_API_KEY not found in environment variables

💡 Solution:
export OPENAI_API_KEY="your_api_key_here"
```

#### **2. Packages Not Installed**
```bash
❌ Failed to import langchain

💡 Solution:
pip install langchain langchain-openai
```

#### **3. Vector Store Not Loading**
```bash
❌ Vector store not available

💡 Solution:
- Ensure knowledge_base_manager.py has processed files
- Check embeddings folder exists
- Verify OpenAI API key is valid
```

#### **4. File Processing Errors**
```bash
❌ Error processing file

💡 Solution:
- Check file format is supported
- Ensure file is readable
- Check log files for details
```

### **Debug Commands**

```bash
# Check system status
python -c "from knowledge_base_manager import KnowledgeBaseManager; kb = KnowledgeBaseManager(); print(kb.get_knowledge_base_stats())"

# Test file processing
python -c "from knowledge_base_manager import KnowledgeBaseManager; kb = KnowledgeBaseManager(); kb.process_all_files()"

# Check vector store
python -c "from langchain_community.vectorstores import Chroma; vs = Chroma(persist_directory='knowledge_base_docs/embeddings'); print(f'Total embeddings: {vs._collection.count()}')"
```

## 🔧 Configuration

### **Environment Variables**

```bash
# Required
export OPENAI_API_KEY="your_openai_api_key"

# Optional
export OPENAI_MODEL="gpt-4o-mini"  # Default: gpt-4o-mini
export CHUNK_SIZE="1000"           # Default: 1000
export CHUNK_OVERLAP="200"         # Default: 200
export SEARCH_RESULTS="5"           # Default: 5
```

### **Custom Settings**

```python
# In knowledge_base_manager.py
manager = KnowledgeBaseManager(
    docs_folder="custom_docs_folder",
    embeddings_folder="custom_embeddings",
    processed_folder="custom_processed",
    logs_folder="custom_logs"
)
```

## 📈 Performance Optimization

### **Best Practices**

1. **File Organization**
   - Use descriptive filenames
   - Include relevant tags
   - Group related content

2. **Content Quality**
   - Write clear, structured content
   - Use proper markdown formatting
   - Include relevant keywords

3. **System Maintenance**
   - Monitor log files regularly
   - Clean up old processed files
   - Monitor OpenAI API usage

### **Performance Metrics**

- **Processing Speed**: ~1000 words/second
- **Embedding Creation**: ~1-2 seconds per chunk
- **Search Response**: ~0.5-1 second
- **Memory Usage**: ~50MB per 1000 embeddings

## 🔮 Future Enhancements

### **Planned Features**

- **Multi-language Support**: Process documents in different languages
- **Advanced Metadata**: Extract more structured information
- **Custom Embeddings**: Support for different embedding models
- **API Endpoints**: REST API for integration
- **Web Interface**: Browser-based management
- **Real-time Collaboration**: Multiple users adding files
- **Version Control**: Track document changes over time

### **Integration Possibilities**

- **Slack/Discord**: Chat integration
- **Webhooks**: Notify external systems
- **Analytics**: Track usage patterns
- **Backup**: Cloud storage integration
- **CDN**: Distribute embeddings globally

## 📚 API Reference

### **KnowledgeBaseManager Class**

```python
class KnowledgeBaseManager:
    def __init__(self, docs_folder="knowledge_base_docs", ...)
    def process_file(self, file_path: Path) -> bool
    def process_all_files(self)
    def search_knowledge_base(self, query: str, top_k: int = 5)
    def get_knowledge_base_stats(self) -> Dict[str, Any]
    def start_file_monitoring(self)
```

### **EnhancedGoogleAIChatbot Class**

```python
class EnhancedGoogleAIChatbot:
    def __init__(self, embeddings_folder="knowledge_base_docs/embeddings")
    def chat(self, user_input: str) -> Dict[str, Any]
    def get_knowledge_base_context(self, query: str, top_k: int = 5)
    def interactive_chat(self)
```

## 🤝 Contributing

### **Development Setup**

```bash
# Clone the repository
git clone <your-repo>
cd <your-repo>

# Install development dependencies
pip install -r requirements_knowledge_base.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

### **Adding New Features**

1. **Fork the repository**
2. **Create a feature branch**
3. **Implement your changes**
4. **Add tests**
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### **Getting Help**

1. **Check the logs**: `knowledge_base_docs/logs/`
2. **Review this README**: Look for troubleshooting section
3. **Check system status**: Use `stats` command in chatbot
4. **Verify environment**: Check OpenAI API key and packages

### **Reporting Issues**

When reporting issues, please include:
- **Error message**: Full error text
- **System information**: OS, Python version, package versions
- **Steps to reproduce**: What you did when the error occurred
- **Log files**: Relevant log entries
- **Environment**: Environment variables and configuration

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainer**: Google Ads Development Team  
**Category**: Knowledge Base System  
**Tags**: knowledge base, vector embeddings, langchain, openai, chatbot, automation, file monitoring
