# Google Ads AI Chat Assistant

This document describes the AI-powered chat assistant integrated into the Google Ads Marketing Assistant project. The chat assistant uses LangChain, OpenAI GPT models, and provides comprehensive tools for managing Google Ads campaigns, analyzing performance data, and accessing company knowledge base.

## 🚀 Features

### Core Chat Functionality
- **Conversational AI**: Natural language interaction with Google Ads data
- **Session Management**: Persistent chat sessions with memory
- **Intent Recognition**: Automatic detection of user intentions
- **Rich UI Responses**: Structured responses with charts, tables, and action buttons

### Google Ads Tools
- **Campaign Management**: Create, pause, resume, and delete campaigns
- **Data Retrieval**: Get campaigns, ad groups, keywords, and performance data
- **Real-time API**: Direct integration with Google Ads API v21
- **Budget Management**: Monitor and analyze budget utilization

### Knowledge Base (RAG)
- **Vector Search**: Semantic search using embeddings
- **Document Management**: Add, search, and retrieve company documents
- **Similarity Matching**: Find relevant information based on user queries

### Analytics & Insights
- **Performance Reports**: Comprehensive campaign performance analysis
- **Budget Insights**: Budget utilization and recommendations
- **Trend Analysis**: Historical data analysis and trends
- **Custom Metrics**: Calculated KPIs and performance indicators

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Django Backend  │    │   Data Stores   │
│                 │    │                  │    │                 │
│ • Chat Interface│◄──►│ • LangChain LLM  │◄──►│ • PostgreSQL   │
│ • Chart.js      │    │ • OpenAI GPT-4   │    │ • pgvector      │
│ • UI Components │    │ • Tools (CRUD)   │    │ • Chat History  │
│ • CTA Buttons   │    │ • Intent Router  │    │ • Company KB    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Google Ads API  │
                       │ • Campaigns      │
                       │ • Ad Groups      │
                       │ • Ads            │
                       │ • Budgets        │
                       └──────────────────┘
```

## 📋 Prerequisites

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Ads Configuration
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
GOOGLE_ADS_CLIENT_ID=your_client_id_here
GOOGLE_ADS_CLIENT_SECRET=your_client_secret_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Python Dependencies
```bash
pip install -r requirements_chat.txt
```

### Database Extensions
```sql
-- Enable vector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;
```

## 🗄️ Database Models

### Chat Models
- **ChatSession**: Manages chat conversation sessions
- **ChatMessage**: Stores individual messages with metadata
- **UserIntent**: Tracks user intent patterns for fine-tuning
- **AIToolExecution**: Logs tool executions for auditing

### Knowledge Base Models
- **KBDocument**: Company documents with vector embeddings
- **Document Types**: General, policy, procedure, FAQ, etc.

### Integration with Existing Models
- **GoogleAdsAccount**: User's Google Ads accounts
- **GoogleAdsCampaign**: Campaign information and status
- **GoogleAdsAdGroup**: Ad group details and performance
- **GoogleAdsPerformance**: Historical performance metrics

## 🛠️ Available Tools

### Google Ads Tools (`GoogleAdsTools`)
- `get_campaigns`: Retrieve campaign information
- `create_campaign`: Create new campaigns with budgets
- `get_ad_groups`: Get ad groups for campaigns
- `pause_campaign`: Pause active campaigns
- `resume_campaign`: Resume paused campaigns

### Database Tools (`DatabaseTools`)
- `search_campaigns_db`: Search local campaign database
- `get_account_summary`: Account overview and statistics
- `get_campaign_performance`: Performance data analysis
- `search_keywords`: Keyword search and analysis

### Knowledge Base Tools (`KnowledgeBaseTools`)
- `search_kb`: Semantic search using vector similarity
- `add_kb_document`: Add documents to knowledge base
- `get_kb_documents`: Retrieve documents by type/company

### Analytics Tools (`AnalyticsTools`)
- `generate_performance_report`: Comprehensive performance analysis
- `get_budget_insights`: Budget utilization and recommendations

## 🔌 API Endpoints

### Chat Endpoints
```
POST   /api/chat/message/           # Send chat message
GET    /api/chat/sessions/          # List chat sessions
POST   /api/chat/sessions/create/   # Create new session
GET    /api/chat/sessions/{id}/     # Get chat history
DELETE /api/chat/sessions/{id}/     # Delete session
```

### Knowledge Base Endpoints
```
POST   /api/kb/add/                 # Add document
GET    /api/kb/search/?q=query      # Search documents
GET    /api/kb/documents/           # List documents
```

### Analytics Endpoints
```
GET    /api/insights/quick/         # Quick insights
GET    /api/insights/context/       # User context
POST   /api/tools/execute/          # Execute specific tool
GET    /api/health/                 # Service health check
```

## 💬 Usage Examples

### Basic Chat Interaction
```python
from google_ads_new.chat_service import ChatService

# Initialize chat service
chat_service = ChatService(user)

# Start session
session_id = chat_service.start_session("Campaign Analysis")

# Send message
response = chat_service.process_message("Show me my top performing campaigns")
print(response)
```

### Direct Tool Execution
```python
from google_ads_new.langchain_tools import GoogleAdsTools

# Initialize tools
ga_tools = GoogleAdsTools(user, session_id)

# Get campaigns
campaigns = ga_tools.get_campaigns(status="ENABLED", limit=10)
print(f"Found {len(campaigns)} active campaigns")
```

### Knowledge Base Search
```python
from google_ads_new.langchain_tools import KnowledgeBaseTools

# Initialize KB tools
kb_tools = KnowledgeBaseTools(user, session_id)

# Search for documents
results = kb_tools.search_kb("refund policy", company_id=1, top_k=5)
print(f"Found {len(results)} relevant documents")
```

## 🎨 Response Format

The chat assistant returns structured responses with UI blocks:

```json
{
  "success": true,
  "session_id": "uuid",
  "response": {
    "blocks": [
      {
        "type": "text",
        "content": "Here are your top campaigns by spend",
        "style": "paragraph"
      },
      {
        "type": "chart",
        "chart_type": "bar",
        "title": "Spend by Campaign (₹)",
        "labels": ["Brand", "Perf", "DSA"],
        "datasets": [
          {
            "label": "Cost",
            "data": [12000, 8000, 5000]
          }
        ]
      },
      {
        "type": "table",
        "title": "Campaigns",
        "columns": ["ID", "Name", "Status", "Cost"],
        "rows": [
          ["111", "Brand", "ENABLED", "₹12,000"],
          ["222", "Perf", "PAUSED", "₹8,000"]
        ]
      },
      {
        "type": "actions",
        "items": [
          {"id": "create_campaign", "label": "Create Campaign"},
          {"id": "pause_high_cpc", "label": "Pause High CPC AdGroup"}
        ]
      }
    ]
  }
}
```

## 🔧 Configuration

### LLM Configuration
```python
# In llm_setup.py
llm = ChatOpenAI(
    model="gpt-4o-mini",  # Use gpt-4o-mini for cost efficiency
    temperature=0.1,       # Low temperature for consistent responses
    openai_api_key=os.getenv('OPENAI_API_KEY')
)
```

### Tool Configuration
```python
# Enable/disable specific tools
ENABLED_TOOLS = [
    'google_ads_get_campaigns',
    'google_ads_create_campaign',
    'db_search_campaigns',
    'kb_search',
    'analytics_performance_report'
]
```

### Memory Configuration
```python
# Chat memory settings
MEMORY_WINDOW = 10  # Remember last 10 messages
SESSION_TIMEOUT = 3600  # Session timeout in seconds
```

## 🧪 Testing

### Run Tests
```bash
# Test chat functionality
python google_ads_new/test_chat.py

# Test specific components
python manage.py test google_ads_new.tests.test_chat
```

### Test Scenarios
1. **Basic Chat**: Simple message exchange
2. **Tool Execution**: Test individual tools
3. **Session Management**: Create, load, delete sessions
4. **Knowledge Base**: Add and search documents
5. **Error Handling**: Test error scenarios

## 🚀 Deployment

### Production Setup
1. **Environment Variables**: Set all required API keys
2. **Database**: Ensure pgvector extension is enabled
3. **Dependencies**: Install all required packages
4. **Migrations**: Run Django migrations
5. **Health Check**: Verify service health endpoint

### Monitoring
- **Tool Execution Logs**: Track AI tool usage
- **User Intent Patterns**: Analyze user behavior
- **Performance Metrics**: Monitor response times
- **Error Rates**: Track and resolve issues

### Scaling Considerations
- **Vector Database**: Consider dedicated vector DB for large KB
- **Caching**: Implement Redis for session storage
- **Async Processing**: Use Celery for long-running operations
- **Rate Limiting**: Implement API rate limiting

## 🔒 Security

### Authentication
- **User Authentication**: Django's built-in auth system
- **Session Security**: Secure session management
- **API Protection**: REST framework permissions

### Data Privacy
- **User Isolation**: Users can only access their own data
- **Audit Logging**: Track all AI tool executions
- **Data Encryption**: Encrypt sensitive information

## 📚 Additional Resources

### Documentation
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Google Ads API v21](https://developers.google.com/google-ads/api/docs/start)

### Examples
- [Chat Examples](examples/chat_examples.md)
- [Tool Usage Examples](examples/tool_examples.md)
- [Response Format Examples](examples/response_examples.md)

### Support
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: Project Wiki

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Submit pull request

### Code Standards
- **Python**: PEP 8 compliance
- **Django**: Follow Django best practices
- **Documentation**: Update docs for new features
- **Testing**: Maintain test coverage

---

**Note**: This chat assistant requires an active OpenAI API key and Google Ads API access to function properly. Ensure all prerequisites are met before deployment.
