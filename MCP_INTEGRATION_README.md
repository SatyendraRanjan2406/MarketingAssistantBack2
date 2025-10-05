# MCP Integration for Google Ads API

## 🎯 Overview

This implementation provides a new `/chat2` endpoint in the ad_expert app that uses **Model Context Protocol (MCP)** to connect to Google Ads APIs. MCP enables standardized communication between AI models and external tools/services.

## 🏗️ Architecture

```
User Request → /chat2 endpoint → MCP Client → MCP Server → Google Ads API
                    ↓
              Conversation Context
                    ↓
              Customer ID Persistence
```

## 📁 Files Created

### 1. **mcp.json** - MCP Configuration
```json
{
  "mcpServers": {
    "google-ads-custom": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/Users/satyendra/marketing_assistant_back",
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "${GOOGLE_ADS_DEVELOPER_TOKEN}",
        "GOOGLE_ADS_CLIENT_ID": "${GOOGLE_ADS_CLIENT_ID}",
        "GOOGLE_ADS_CLIENT_SECRET": "${GOOGLE_ADS_CLIENT_SECRET}",
        "GOOGLE_ADS_REFRESH_TOKEN": "${GOOGLE_ADS_REFRESH_TOKEN}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

### 2. **mcp_server.py** - Custom MCP Server
- **Purpose**: Provides Google Ads API access through MCP protocol
- **Features**:
  - Tool definitions for Google Ads operations
  - Async tool execution
  - Error handling and logging
  - Integration with existing Django models

**Available Tools**:
- `get_overview` - Get account overview and summary
- `get_campaigns` - Retrieve Google Ads campaigns
- `get_campaign_by_id` - Get specific campaign by ID with details
- `get_campaigns_with_filters` - Get campaigns with specific filters
- `create_campaign` - Create new campaigns with budgets
- `get_ads` - Get ads for campaigns
- `get_ad_by_id` - Get specific ad by ID with details
- `get_ads_with_filters` - Get ads with specific filters
- `get_ads_by_campaign_id` - Get all ads for a specific campaign
- `get_ad_groups` - Get ad groups (adsets) information
- `get_ad_group_by_id` - Get specific ad group by ID with details
- `get_ad_groups_with_filters` - Get ad groups with specific filters
- `get_ad_groups_by_campaign_id` - Get all ad groups for a specific campaign
- `create_ad` - Create new ads
- `pause_campaign` - Pause active campaigns
- `resume_campaign` - Resume paused campaigns
- `get_performance_data` - Get performance metrics
- `get_keywords` - Fetch keywords for ad groups
- `get_budgets` - Get budget information
- `get_budget_by_id` - Get specific budget by ID with details
- `get_budgets_with_filters` - Get budgets with specific filters
- `get_budgets_by_campaign_id` - Get all budgets for a specific campaign
- `get_accessible_customers` - List accessible customer accounts

### 3. **ad_expert/mcp_client.py** - MCP Client Service
- **Purpose**: Handles communication with MCP server
- **Features**:
  - Server lifecycle management
  - Tool call orchestration
  - High-level Google Ads operations
  - Performance data summarization

### 4. **RAGChat2View** - New API Endpoint
- **URL**: `/ad-expert/api/chat2/`
- **Features**:
  - Customer ID persistence (reuses existing logic)
  - Intent mapping integration
  - MCP service initialization
  - Structured response format

## 🔧 Setup Requirements

### Dependencies
```bash
pip install mcp
```

### Environment Variables
```bash
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Usage Examples

### 1. Get Accessible Customers
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat2/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me my accessible Google Ads customers"}'
```

### 2. Select Customer and Get Campaigns
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat2/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Use customers/9631603999 and show me my campaigns",
    "conversation_id": 123
  }'
```

### 3. Get Ad Groups (Customer ID Persisted)
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat2/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me ad groups for my campaigns",
    "conversation_id": 123
  }'
```

## 📊 Response Structure

```json
{
  "success": true,
  "intent_mapping": {
    "actions": ["GET_CAMPAIGNS"],
    "confidence": 0.95,
    "reasoning": "User is asking for campaign data"
  },
  "chat_response": "I retrieved 5 campaigns for customer customers/9631603999...",
  "mcp_result": {
    "content": "I retrieved 5 campaigns...",
    "data": {
      "success": true,
      "customer_id": "customers/9631603999",
      "campaigns": [...],
      "total_count": 5,
      "performance_summary": {
        "total_impressions": 10000,
        "total_clicks": 500,
        "total_cost": 150.50,
        "average_ctr": 5.0,
        "average_cpc": 0.30
      }
    },
    "type": "campaign_data"
  },
  "stored_customer_id": "customers/9631603999",
  "customer_selection_required": false,
  "conversation_id": 123,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔄 MCP Tool Execution Flow

1. **User Query**: "Show me my campaigns"
2. **Intent Mapping**: Identifies `GET_CAMPAIGNS` action
3. **Customer ID Check**: Uses stored customer ID or prompts for selection
4. **MCP Tool Call**: Calls `get_campaigns` tool via MCP server
5. **Google Ads API**: Server queries Google Ads API
6. **Data Processing**: Results are processed and enhanced
7. **Response**: Structured data returned to user

## 🛠️ Key Features

### 1. **Customer ID Persistence**
- Customer ID stored in conversation model
- Automatically used in all subsequent requests
- No repeated customer selection prompts

### 2. **Intent-Driven Processing**
- Leverages existing intent mapping service
- Routes requests to appropriate MCP tools
- Maintains context across conversation

### 3. **Comprehensive Data Retrieval**
- Campaign data with performance metrics
- Ad group information and statistics
- Keyword data and performance
- Flexible date range support

### 4. **Error Handling**
- Graceful MCP server initialization
- Comprehensive error logging
- Fallback responses for failed operations

### 5. **Performance Optimization**
- Async MCP operations
- Data summarization and aggregation
- Efficient API call management

## 🧪 Testing

Run the test script to verify MCP integration:
```bash
python test_mcp_chat2.py
```

The test covers:
- MCP server initialization
- Customer ID persistence
- Campaign data retrieval
- Ad group data fetching
- Error handling scenarios

## 🔍 Monitoring and Logging

The implementation includes comprehensive logging:
- MCP server lifecycle events
- Tool execution results
- Error conditions and stack traces
- Performance metrics and timing

## 🚀 Benefits of MCP Integration

1. **Standardized Protocol**: Uses industry-standard MCP for tool communication
2. **Modular Architecture**: Separates concerns between client and server
3. **Extensibility**: Easy to add new Google Ads operations
4. **Maintainability**: Clean separation of MCP logic from Django views
5. **Scalability**: MCP server can be deployed independently if needed

## 🔧 Troubleshooting

### Common Issues

1. **MCP Server Not Starting**
   - Check environment variables
   - Verify Google Ads credentials
   - Check Python dependencies

2. **Tool Execution Failures**
   - Verify customer ID format
   - Check Google Ads API permissions
   - Review error logs for details

3. **Authentication Issues**
   - Ensure JWT token is valid
   - Check user has Google OAuth connection
   - Verify accessible customers exist

## 📈 Future Enhancements

- **Caching**: Add Redis caching for frequently accessed data
- **Rate Limiting**: Implement API rate limiting
- **Webhooks**: Add real-time data updates via webhooks
- **Analytics**: Enhanced performance analytics and insights
- **Multi-Account**: Support for multiple Google Ads accounts simultaneously

## 🎯 Conclusion

The MCP integration provides a robust, scalable solution for Google Ads API access through the Model Context Protocol. It maintains all existing functionality while adding the benefits of standardized tool communication and improved architecture.

The `/chat2` endpoint is now ready for production use with full Google Ads API integration via MCP! 🎉
