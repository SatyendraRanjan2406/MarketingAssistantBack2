# RAG System for Google Ads Analysis

## 🚀 **Overview**

The RAG (Retrieval-Augmented Generation) system enhances Google Ads analysis by combining authoritative knowledge from a vector database with intelligent AI responses. This system provides context-aware, expert-level recommendations based on industry best practices and real-world case studies.

## 🏗️ **Architecture**

### **Core Components**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query   │───▶│  Smart Context   │───▶│  RAG Service    │
│                │    │   Selection      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Vector Store    │    │   OpenAI API    │
                       │   (Chroma)       │    │                 │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Knowledge Base  │    │  Response Gen   │
                       │   Documents      │    │                 │
                       └──────────────────┘    └─────────────────┘
```

### **Key Features**

- **🔍 Smart Context Selection**: Automatically decides between RAG and direct OpenAI
- **📚 Vector Database**: Chroma-based document storage with semantic search
- **🧠 Intelligent Retrieval**: Context-aware document search and retrieval
- **🔄 Hybrid Responses**: Combines knowledge base context with AI generation
- **⚡ Fallback Strategy**: Graceful degradation when RAG is not helpful

## 🛠️ **Installation & Setup**

### **1. Install Dependencies**

```bash
pip install -r requirements.txt
```

**Required Packages:**
- `chromadb>=0.4.0` - Vector database
- `langchain>=0.1.0` - Document processing framework
- `langchain-openai>=0.0.5` - OpenAI integration
- `sentence-transformers>=2.2.0` - Local embeddings fallback
- `tiktoken>=0.5.0` - Token counting
- `pypdf>=3.0.0` - PDF document processing
- `python-docx>=0.8.11` - Word document processing

### **2. Setup RAG System**

```bash
python setup_rag_system.py
```

This script will:
- Initialize the vector database
- Create sample knowledge base documents
- Test the RAG system functionality
- Verify all components are working

### **3. Test RAG System**

```bash
python demo_rag_system.py
```

This demo showcases:
- Smart context selection
- Document search and retrieval
- RAG vs Direct OpenAI comparison
- Hybrid response generation
- Context augmentation

## 📚 **Knowledge Base Management**

### **Document Types Supported**

| Format | Extension | Loader | Use Case |
|--------|-----------|---------|----------|
| Text | `.txt` | `TextLoader` | Simple text documents |
| Markdown | `.md` | `UnstructuredMarkdownLoader` | Documentation, guides |
| PDF | `.pdf` | `PDFLoader` | Reports, whitepapers |
| Word | `.docx` | `Docx2txtLoader` | Business documents |
| CSV | `.csv` | `CSVLoader` | Data tables, reports |

### **Adding Documents**

1. **Place files in `knowledge_base/` directory**
2. **Documents are automatically processed on system startup**
3. **Vector embeddings are generated and stored**
4. **Documents become searchable immediately**

### **Document Structure**

```
knowledge_base/
├── google_ads_best_practices.md    # Best practices guide
├── google_ads_case_studies.md      # Success stories
├── google_ads_basics.txt           # Basic concepts
├── success_case_study.txt          # Case studies
└── custom_documents/               # Your custom content
    ├── industry_guides/
    ├── company_policies/
    └── training_materials/
```

### **Document Metadata**

Each document chunk includes:
- **Source**: Document identifier
- **Added At**: Timestamp of addition
- **User ID**: Associated user
- **Content**: Text content for search

## 🔧 **API Usage**

### **Basic RAG Service**

```python
from google_ads_new.rag_service import GoogleAdsRAGService

# Initialize service
rag_service = GoogleAdsRAGService(user)

# Add documents
rag_service.add_text_file("path/to/document.txt", "source_name")
rag_service.add_markdown_file("path/to/guide.md", "source_name")

# Search documents
results = rag_service.search_documents("query", k=5)

# Get hybrid response
response = rag_service.get_hybrid_response("user query", user_data)
```

### **Smart Context Selection**

```python
# Automatically decide RAG vs Direct OpenAI
context, use_rag = rag_service.smart_context_selection(query, user_data)

if use_rag:
    # Use RAG with context
    response = rag_service.get_rag_response(query, context, user_data)
else:
    # Use direct OpenAI
    response = rag_service.get_direct_openai_response(query, user_data)
```

### **Document Operations**

```python
# Add different document types
rag_service.add_text_file("file.txt", "source")
rag_service.add_pdf_file("file.pdf", "source")
rag_service.add_markdown_file("file.md", "source")
rag_service.add_csv_file("file.csv", "source")

# Search with filters
results = rag_service.search_documents(
    "query", 
    k=5, 
    filters={"source": "best_practices"}
)

# Get vector store statistics
stats = rag_service.get_vectorstore_stats()

# Clear vector store (reset)
rag_service.clear_vectorstore()
```

## 🧠 **Smart Context Selection**

### **Decision Logic**

The system automatically decides when to use RAG based on:

#### **RAG is Helpful When:**
- ✅ **Knowledge Requirements**: Query asks for best practices, guidelines, strategies
- ✅ **Complex Queries**: Long or multi-part questions
- ✅ **Strategic Questions**: Planning, methodology, approach questions
- ✅ **Limited User Data**: User has few campaigns or limited data
- ✅ **Industry Knowledge**: Questions requiring expert domain knowledge

#### **Direct OpenAI is Better When:**
- ✅ **Simple Queries**: Short, direct questions
- ✅ **Data Analysis**: Performance metrics, campaign data analysis
- ✅ **Action Requests**: Create, update, delete operations
- ✅ **User-Specific Data**: Questions about user's own campaigns
- ✅ **Real-time Information**: Current performance, immediate actions

### **Query Analysis**

The system analyzes queries based on:

```python
query_analysis = {
    "length": len(query),
    "complexity": "simple|medium|complex",
    "type": "general|knowledge|data",
    "requires_knowledge": bool,
    "requires_data": bool
}
```

### **Selection Examples**

| Query | Analysis | Selection | Reason |
|-------|----------|-----------|---------|
| "What are best practices for campaign structure?" | Knowledge, Complex | RAG | Requires industry expertise |
| "Show my campaign performance" | Data, Simple | Direct | User-specific data analysis |
| "How do I optimize Quality Score?" | Knowledge, Medium | RAG | Strategy question |
| "Create new campaign" | Action, Simple | Direct | Simple action request |
| "What bidding strategy works for e-commerce?" | Knowledge, Complex | RAG | Industry knowledge needed |

## 🔍 **Document Search & Retrieval**

### **Search Process**

1. **Query Processing**: Analyze user query for intent and keywords
2. **Semantic Search**: Find relevant documents using vector similarity
3. **Context Building**: Extract relevant content from retrieved documents
4. **Context Truncation**: Intelligently truncate context to fit token limits
5. **Response Generation**: Generate AI response with augmented context

### **Search Parameters**

```python
# Basic search
results = rag_service.search_documents("query", k=5)

# Search with filters
results = rag_service.search_documents(
    "query",
    k=5,
    filters={
        "source": "best_practices",
        "user_id": "user_123"
    }
)
```

### **Context Building**

The system builds context by:
- **Document Content**: Relevant text from retrieved documents
- **User Data**: User's campaign information and performance
- **Query Context**: Original user question
- **Metadata**: Source information and timestamps

### **Context Truncation**

When context exceeds token limits:
- **Intelligent Truncation**: Preserves most relevant content
- **Length Indicators**: Shows total available context
- **Source Preservation**: Maintains document source information

## 🎯 **Response Generation**

### **RAG-Enhanced Responses**

```python
# Generate RAG response with context
response = rag_service.get_rag_response(query, context, user_data)

# Response includes:
response = {
    "blocks": [...],           # UI blocks for frontend
    "rag_metadata": {
        "context_used": True,
        "context_length": 2500,
        "context_sources": ["best_practices", "case_studies"],
        "generation_method": "rag"
    }
}
```

### **Direct OpenAI Responses**

```python
# Generate direct response without context
response = rag_service.get_direct_openai_response(query, user_data)

# Response includes:
response = {
    "blocks": [...],           # UI blocks for frontend
    "rag_metadata": {
        "context_used": False,
        "context_length": 0,
        "context_sources": [],
        "generation_method": "direct"
    }
}
```

### **Hybrid Responses**

```python
# Get best of both worlds
response = rag_service.get_hybrid_response(query, user_data)

# Response includes:
response = {
    "blocks": [...],           # UI blocks for frontend
    "response_type": "rag_enhanced|direct_openai",
    "hybrid_metadata": {
        "context_selection": "rag|direct",
        "context_length": 2500,
        "selection_reason": "Detailed explanation"
    },
    "rag_metadata": {...}      # RAG-specific metadata
}
```

## 🎨 **Frontend Integration**

### **Chat Interface Updates**

The frontend has been updated to handle RAG responses:

```typescript
// Handle RAG-enhanced responses
case 'rag_enhanced_response':
  return (
    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-4">
      <div className="flex items-center mb-2">
        <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
        <span className="text-sm text-purple-600 font-medium">
          RAG-Enhanced AI Response
        </span>
      </div>
      <div className="text-sm text-purple-700 mb-3">
        {block.fallback_message || "Generated RAG-enhanced AI response"}
      </div>
      <div className="mt-3">
        <AnalysisBlock
          type="rag_enhanced"
          title="AI Analysis with Knowledge Base"
          data={block.data || block}
          account={block.account}
          timestamp={block.timestamp}
        />
      </div>
    </div>
  );
```

### **Analysis Block Updates**

The `AnalysisBlock` component handles RAG responses:

```typescript
case 'rag_enhanced':
  // Handle RAG-enhanced responses with blocks structure
  if (data.blocks && Array.isArray(data.blocks)) {
    return (
      <div className="space-y-4">
        {data.blocks.map((block: any, index: number) => (
          <div key={index} className="border-l-4 border-purple-400 pl-4">
            {renderOpenAIBlock(block)}
          </div>
        ))}
      </div>
    );
  }
  // Fallback for other RAG response formats
  return (
    <div className="space-y-4">
      {Object.entries(data).map(([key, value]) => {
        if (key in ['success', 'account', 'timestamp', 'error']) return null;
        return renderAnalysisItem(key, value as AnalysisItem);
      })}
    </div>
  );
```

## 📊 **Performance & Monitoring**

### **Vector Store Statistics**

```python
stats = rag_service.get_vectorstore_stats()

# Returns:
{
    "total_documents": 150,
    "embedding_dimension": 1536,
    "database_path": "/path/to/vector_db",
    "last_updated": "2024-01-15T10:30:00"
}
```

### **Performance Metrics**

- **Search Speed**: Document retrieval time
- **Context Quality**: Relevance of retrieved content
- **Response Time**: Total generation time
- **Token Usage**: Context and response token counts
- **Selection Accuracy**: RAG vs Direct decision accuracy

### **Monitoring & Optimization**

1. **Regular Performance Reviews**: Monitor response times and quality
2. **Context Quality Analysis**: Review retrieved document relevance
3. **Selection Logic Tuning**: Optimize RAG vs Direct decisions
4. **Document Quality**: Ensure knowledge base relevance and accuracy

## 🔒 **Security & Privacy**

### **Data Protection**

- **User Isolation**: Each user has isolated vector store
- **Document Access Control**: Users only access their own documents
- **API Key Security**: OpenAI API key stored in environment variables
- **No Data Persistence**: Vector embeddings are temporary

### **Privacy Considerations**

- **Document Content**: Only document content is embedded
- **User Data**: User-specific data is not stored in vector store
- **Search Privacy**: Search queries are not logged
- **Response Privacy**: AI responses are not stored

## 🚀 **Advanced Features**

### **Custom Embeddings**

```python
# Use custom embedding models
from sentence_transformers import SentenceTransformer

custom_embeddings = SentenceTransformer('all-MiniLM-L6-v2')
rag_service = GoogleAdsRAGService(user, embeddings=custom_embeddings)
```

### **Document Preprocessing**

```python
# Custom document processing
def custom_preprocessor(text):
    # Custom text cleaning and processing
    return cleaned_text

rag_service.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    preprocessor=custom_preprocessor
)
```

### **Advanced Filtering**

```python
# Complex document filtering
filters = {
    "source": {"$in": ["best_practices", "case_studies"]},
    "added_at": {"$gte": "2024-01-01"},
    "user_id": "user_123"
}

results = rag_service.search_documents("query", k=5, filters=filters)
```

## 🧪 **Testing & Debugging**

### **Unit Tests**

```python
# Test RAG service functionality
def test_rag_service():
    rag_service = GoogleAdsRAGService(test_user)
    
    # Test document addition
    chunks_added = rag_service.add_text_file("test.txt", "test")
    assert chunks_added > 0
    
    # Test search
    results = rag_service.search_documents("test query")
    assert len(results) > 0
    
    # Test context selection
    context, use_rag = rag_service.smart_context_selection("test", {})
    assert isinstance(use_rag, bool)
```

### **Integration Tests**

```python
# Test complete RAG workflow
def test_rag_workflow():
    rag_service = GoogleAdsRAGService(test_user)
    
    # Setup test data
    setup_test_documents(rag_service)
    
    # Test hybrid response
    response = rag_service.get_hybrid_response("test query", {})
    
    # Verify response structure
    assert "blocks" in response
    assert "response_type" in response
    assert "hybrid_metadata" in response
```

### **Debug Mode**

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug RAG service
rag_service = GoogleAdsRAGService(user)
rag_service.debug = True
```

## 🔮 **Future Enhancements**

### **Planned Features**

1. **Multi-Modal Support**: Image and video document processing
2. **Real-time Updates**: Live document synchronization
3. **Advanced Analytics**: Detailed performance insights
4. **Custom Models**: Fine-tuned embedding models
5. **Collaborative Features**: Shared knowledge bases

### **Scalability Improvements**

1. **Distributed Vector Store**: Multi-node Chroma deployment
2. **Caching Layer**: Redis-based response caching
3. **Async Processing**: Background document processing
4. **Load Balancing**: Multiple RAG service instances

### **Integration Opportunities**

1. **External APIs**: Google Ads API integration
2. **Third-party Tools**: SEMrush, Ahrefs integration
3. **CRM Systems**: Salesforce, HubSpot integration
4. **Analytics Platforms**: Google Analytics, Mixpanel integration

## 📚 **Best Practices**

### **Knowledge Base Management**

1. **Regular Updates**: Keep documents current and relevant
2. **Quality Control**: Ensure accuracy and completeness
3. **Source Attribution**: Maintain proper source information
4. **Version Control**: Track document changes and updates

### **Performance Optimization**

1. **Chunk Size**: Optimize document chunk sizes for your use case
2. **Overlap Settings**: Balance context with token efficiency
3. **Search Parameters**: Tune search parameters for relevance
4. **Context Limits**: Set appropriate context length limits

### **User Experience**

1. **Clear Indicators**: Show when RAG vs Direct is used
2. **Source Attribution**: Display knowledge base sources
3. **Context Preview**: Allow users to see retrieved context
4. **Feedback Collection**: Gather user feedback on response quality

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python version compatibility
python --version  # Should be 3.8+
```

#### **Vector Store Issues**
```python
# Clear and recreate vector store
rag_service.clear_vectorstore()

# Check file permissions
import os
print(os.access("vector_db", os.W_OK))
```

#### **Document Processing Errors**
```python
# Check document format
from pathlib import Path
file_path = Path("document.txt")
print(f"File exists: {file_path.exists()}")
print(f"File size: {file_path.stat().st_size}")

# Test document loader
from langchain.document_loaders import TextLoader
loader = TextLoader("document.txt")
documents = loader.load()
print(f"Documents loaded: {len(documents)}")
```

#### **OpenAI API Issues**
```python
# Check API key
import os
api_key = os.getenv('OPENAI_API_KEY')
print(f"API key present: {bool(api_key)}")
print(f"API key format: {api_key[:10]}..." if api_key else "None")

# Test OpenAI connection
import openai
client = openai.OpenAI(api_key=api_key)
try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("OpenAI connection successful")
except Exception as e:
    print(f"OpenAI connection failed: {e}")
```

### **Performance Issues**

#### **Slow Search**
- Reduce search result count (`k` parameter)
- Optimize document chunk sizes
- Use more specific search queries
- Implement search result caching

#### **High Token Usage**
- Reduce context length limits
- Optimize document chunk overlap
- Use more efficient embedding models
- Implement context truncation

#### **Memory Issues**
- Reduce vector store size
- Clear unused documents
- Use smaller embedding models
- Implement document cleanup

## 📞 **Support & Community**

### **Getting Help**

1. **Documentation**: Review this README thoroughly
2. **Demo Scripts**: Run `demo_rag_system.py` for examples
3. **Setup Scripts**: Use `setup_rag_system.py` for troubleshooting
4. **Logs**: Check Django and Python logs for errors

### **Contributing**

1. **Report Issues**: Document bugs and feature requests
2. **Share Knowledge**: Contribute to knowledge base
3. **Improve Code**: Submit pull requests and improvements
4. **Documentation**: Help improve documentation and examples

---

## 🎉 **Conclusion**

The RAG system provides a powerful foundation for intelligent Google Ads analysis by combining authoritative knowledge with AI-powered insights. The smart context selection ensures optimal response quality while maintaining performance and user experience.

**Key Benefits:**
- 🧠 **Intelligent Responses**: Context-aware, expert-level recommendations
- ⚡ **Smart Selection**: Automatic RAG vs Direct OpenAI decision
- 📚 **Knowledge Base**: Comprehensive Google Ads best practices
- 🔄 **Hybrid Approach**: Best of both worlds for optimal results
- 🎯 **User Experience**: Seamless integration with existing chat interface

**Start using the RAG system today to enhance your Google Ads analysis capabilities!** 🚀

