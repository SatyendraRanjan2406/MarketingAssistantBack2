# LanggraphView - Advanced LangGraph Implementation

## Overview

The `LanggraphView` is an advanced implementation of LangGraph that provides continuous feedback loops, sophisticated state management, and both short-term and long-term memory capabilities. It integrates all Google Ads tools and uses ChatGPT-4o as the chat model.

## Key Features

### 🔄 Continuous Feedback Loops
- **Context Node**: Enriches conversation with user-specific data
- **Chat Node**: Processes messages with LLM and tool binding
- **Tool Node**: Executes Google Ads API tools
- **Decision Node**: Determines next step based on current state

### 💾 Memory Management
- **Short-term Memory**: Uses `MemorySaver` checkpointer for conversation state
- **Long-term Memory**: Uses `PostgresStore` for persistent user data across conversations
- **Thread-based Checkpointing**: Each conversation gets a unique thread ID

### 🛠️ Tool Integration
All Google Ads tools from `ALL_TOOLS` are integrated:
- `get_campaigns` - Get campaign data
- `get_campaign_by_id` - Get specific campaign details
- `get_ad_groups` - Get ad group data
- `get_ads` - Get ad data
- `get_keywords` - Get keyword data
- `get_performance_data` - Get performance metrics
- `get_budgets` - Get budget information
- `get_account_overview` - Get account overview
- `get_search_terms` - Get search terms data
- `get_demographic_data` - Get demographic insights
- `get_geographic_data` - Get geographic data

## Architecture

### State Graph Flow

```
START → context → chat → tools → chat → END
         ↓        ↓      ↓      ↓
      enrich   process  execute continue
      context  message  tools   conversation
```

### State Structure

```python
class LangGraphState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    user_id: int
    conversation_id: Optional[str]
    customer_id: Optional[str]
    accessible_customers: List[str]
    user_context: Dict[str, Any]
    current_step: str
    error_count: int
    max_retries: int
```

### Node Functions

#### 1. Context Node
- **First Priority**: Checks long-term memory for accessible customer IDs
- **Fallback**: Fetches accessible customer IDs from database if not in memory
- **Storage**: Automatically saves accessible customer IDs to long-term memory
- **Enrichment**: Adds user preferences, history, and context to state

#### 2. Chat Node
- Processes user messages with ChatGPT-4o
- Binds all available tools
- Generates responses with tool calls when needed

#### 3. Tool Node
- Executes tool calls from the LLM
- Handles Google Ads API interactions
- Returns tool results to continue conversation

#### 4. Decision Node
- Determines next step based on current state
- Handles error recovery and retry logic
- Manages conversation flow control

## Usage

### API Endpoint
```
POST /api/langgraph/chat/
```

### Request Format
```json
{
    "query": "Show me my campaign performance for last 7 days",
    "conversation_id": "optional_conversation_id",
    "customer_id": "optional_customer_id"
}
```

### Response Format
```json
{
    "message_id": 123,
    "conversation_id": 456,
    "response": "Here's your campaign performance...",
    "langgraph_state": {
        "current_step": "tools_completed",
        "error_count": 0,
        "accessible_customers": ["customers/1234567890"]
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## Configuration

### Short-term Memory (Checkpoints)
```python
# Uses MemorySaver for conversation state
self.checkpointer = MemorySaver()

# Thread ID format: user_{user_id}_conv_{conversation_id}
config = {
    "configurable": {
        "thread_id": f"user_{user_id}_conv_{conversation_id}"
    }
}
```

### Long-term Memory (Multi-layer Storage)
```python
# 1. Redis for fast access
RedisService.save_accessible_customers(user_id, customers)

# 2. Database for persistence
UserGoogleAuth.accessible_customers = {"customers": customers}

# 3. PostgresStore for advanced storage (if available)
self.postgres_store = PostgresSaver.from_conn_string(db_url)
```

### Accessible Customer Management
The system automatically manages accessible customer IDs:

1. **First Check**: Looks in long-term memory (Redis + Database)
2. **Fallback**: Fetches from `UserGoogleAuth` model if not cached
3. **Storage**: Saves to multiple storage layers for reliability
4. **Retrieval**: Fast access from Redis, persistent storage in database

## Error Handling

### Retry Logic
- Maximum 3 retries per conversation
- Error count tracked in state
- Graceful degradation on failures

### Error Recovery
- Context errors → Continue to chat
- Tool errors → Retry with error message
- Chat errors → Increment error count

## Integration with Existing System

### Authentication
- Uses JWT authentication
- Integrates with existing user system
- Maintains conversation persistence

### Database Integration
- Uses existing `Conversation` and `ChatMessage` models
- Stores structured data in `structured_data` field
- Maintains conversation history

### OAuth Integration
- Fetches accessible customers from `UserGoogleAuth`
- Maintains customer ID selection
- Supports multi-account scenarios

## Testing

Run the test script to verify functionality:
```bash
python test_langgraph_view.py
```

The test script will:
- Initialize the LanggraphView
- Test graph structure and flow
- Verify tool integration
- Test memory management
- Demonstrate error handling

## Comparison with Other Views

| Feature | LanggraphView | LangChainView | RAGChatView |
|---------|---------------|---------------|-------------|
| State Management | ✅ Advanced | ❌ Basic | ❌ Basic |
| Memory | ✅ Short + Long | ❌ None | ❌ None |
| Feedback Loops | ✅ Continuous | ❌ Single | ❌ Single |
| Error Recovery | ✅ Advanced | ❌ Basic | ❌ Basic |
| Tool Integration | ✅ All Tools | ✅ All Tools | ❌ Limited |
| Checkpointing | ✅ Thread-based | ❌ None | ❌ None |

## Benefits

1. **Persistent Conversations**: State is maintained across requests
2. **Intelligent Flow Control**: Dynamic decision making based on context
3. **Error Resilience**: Automatic retry and recovery mechanisms
4. **Memory Efficiency**: Short-term for speed, long-term for persistence
5. **Tool Orchestration**: Seamless integration of all Google Ads tools
6. **User Context**: Personalized responses based on user history
7. **Automatic Customer Management**: Accessible customer IDs are automatically cached and retrieved
8. **Multi-layer Storage**: Redis for speed, database for persistence, PostgresStore for advanced features
9. **Smart Caching**: Avoids redundant database queries by checking memory first

## Future Enhancements

1. **Streaming Responses**: Real-time response streaming
2. **Custom Tool Creation**: Dynamic tool registration
3. **Advanced Analytics**: Conversation flow analytics
4. **Multi-modal Support**: Image and document processing
5. **Performance Optimization**: Caching and optimization strategies

## Dependencies

- `langgraph` - Core graph framework
- `langchain` - LLM integration
- `langchain-core` - Core components
- `psycopg2` - PostgreSQL support (for PostgresStore)
- `django` - Web framework
- `djangorestframework` - API framework

## Troubleshooting

### Common Issues

1. **PostgresStore Not Available**
   - Ensure PostgreSQL is configured in Django settings
   - Check database connection string
   - Falls back to in-memory store automatically

2. **Tool Execution Errors**
   - Verify Google Ads API credentials
   - Check customer ID permissions
   - Review tool function implementations

3. **Memory Issues**
   - Monitor checkpoint storage
   - Implement cleanup strategies
   - Consider memory limits

### Debug Mode

Enable debug logging to trace execution:
```python
import logging
logging.getLogger('ad_expert.views').setLevel(logging.DEBUG)
```

## Conclusion

The `LanggraphView` represents a significant advancement in conversational AI for Google Ads management, providing sophisticated state management, persistent memory, and intelligent tool orchestration. It's designed to handle complex, multi-step conversations while maintaining context and providing reliable, error-resilient responses.

