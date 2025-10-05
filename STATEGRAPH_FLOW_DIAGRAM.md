# LangGraph StateGraph Flow Diagram

## Overview
The StateGraph implements a sophisticated multi-stage workflow for Google Ads data analysis and visualization.

## Flow Structure

```
START
  ↓
[context] → context_node
  ↓ (decision_node)
[chat] → chat_node (LLM with tools)
  ↓ (decision_node)
[tools] → tool_node (Google Ads API calls)
  ↓ (decision_node)
[data_analysis] → data_analysis_node (GPT-4o analysis)
  ↓ (decision_node)
[report_generation] → report_generation_node (Formatted reports)
  ↓ (decision_node)
END
```

## Detailed Node Descriptions

### 1. **context_node**
- **Purpose**: Enriches conversation with user context and accessible customers
- **Actions**:
  - Loads conversation history
  - Gets accessible customer IDs
  - Detects customer ID selections
  - Builds system prompt with context
- **Output**: `current_step = "context_enriched"`

### 2. **chat_node**
- **Purpose**: Main LLM interaction with tool access
- **Actions**:
  - Processes user messages with GPT-4o
- **Tools Available**: 15 tools including:
  - Google Ads API tools (campaigns, ads, keywords, etc.)
  - Image generation tools (generate_image, improve_image)
  - Visualization tools (create_data_visualization, format_tabular_data)
- **Output**: `current_step = "chat_completed"`

### 3. **tool_node**
- **Purpose**: Executes Google Ads API calls and other tools
- **Actions**:
  - Calls Google Ads API tools with automatic token refresh
  - Generates images using DALL-E 3
  - Creates data visualizations
  - Formats tabular data
- **Output**: `current_step = "tools_completed"`

### 4. **data_analysis_node**
- **Purpose**: Analyzes fetched data using GPT-4o
- **Trigger**: When user query contains analysis keywords
- **Keywords**: ["analyze", "analysis", "compare", "comparison", "insights", "report", "strategy", "recommendations", "performance", "trends"]
- **Actions**:
  - Takes tool results and user query
  - Uses GPT-4o to generate detailed analysis
  - Provides insights and recommendations
- **Output**: `current_step = "analysis_completed"`

### 5. **report_generation_node**
- **Purpose**: Formats analysis into comprehensive reports
- **Actions**:
  - Creates structured reports with sections:
    1. Executive Summary
    2. Performance Overview
    3. Detailed Analysis
    4. Recommendations
    5. Visual Suggestions
    6. Images (using OpenAI)
    7. Tabular Formatting
    8. Data Visualization
- **Output**: `current_step = "report_completed"`

## Decision Logic (decision_node)

### Flow Control
```python
if error_count >= max_retries:
    return "end"

if current_step == "start":
    return "context"
elif current_step == "context_enriched":
    return "chat"
elif current_step == "chat_completed":
    if has_tool_calls:
        return "tools"
    else:
        return "end"
elif current_step == "tools_completed":
    if analysis_keywords_in_query:
        return "data_analysis"
    else:
        return "chat"
elif current_step == "analysis_completed":
    return "report_generation"
elif current_step == "report_completed":
    return "end"
```

## State Management

### LangGraphState Structure
```python
class LangGraphState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    user_id: int
    customer_id: Optional[str]
    accessible_customers: List[str]
    current_step: str
    error_count: int
    max_retries: int
    conversation_id: Optional[int]
```

### Memory Management
- **Short-term Memory**: MemorySaver checkpointer with thread_id
- **Long-term Memory**: PostgresStore for persistent storage
- **Conversation History**: Loads last 20 messages from database

## Example Flow Scenarios

### Scenario 1: Simple Query
```
User: "What campaigns do I have?"
Flow: START → context → chat → END
Result: Direct response with campaign list
```

### Scenario 2: Data Analysis Request
```
User: "Analyze my campaign performance"
Flow: START → context → chat → tools → data_analysis → report_generation → END
Result: Comprehensive analysis with insights and recommendations
```

### Scenario 3: Image Generation
```
User: "Create a marketing poster"
Flow: START → context → chat → tools → END
Result: Generated image with direct DALL-E URL
```

### Scenario 4: Visualization Request
```
User: "Show me a pie chart of campaign spend"
Flow: START → context → chat → tools → END
Result: Pie chart visualization with direct ChatGPT URL
```

## Key Features

### 1. **Automatic Token Refresh**
- Detects 401/403 errors
- Refreshes OAuth tokens automatically
- Retries failed requests

### 2. **Customer ID Persistence**
- Detects customer ID from user input
- Saves to conversation model
- Maintains context across turns

### 3. **Multi-Stage Analysis**
- Data fetching → Analysis → Report generation
- Conditional routing based on user intent
- Comprehensive insights and recommendations

### 4. **Visual Content Generation**
- Images: DALL-E 3 with direct URLs
- Charts: Pie charts, bar graphs, line charts
- Tables: Markdown and HTML formatting

### 5. **Error Handling**
- Graceful error recovery
- Maximum retry limits
- Fallback mechanisms

## Tools Integration

### Google Ads Tools (11 tools)
- get_campaigns, get_campaign_by_id
- get_ad_groups, get_ads, get_keywords
- get_performance_data, get_budgets
- get_account_overview, get_search_terms
- get_demographic_data, get_geographic_data

### Image & Visualization Tools (4 tools)
- generate_image, improve_image
- create_data_visualization, format_tabular_data

## Memory Persistence

### Short-term Memory
- Thread ID: `user_{user_id}_langgraph`
- Checkpoints at every step
- Conversation state preservation

### Long-term Memory
- PostgresStore for user-specific data
- Accessible customers list
- Customer ID selections
- Conversation history

This StateGraph provides a robust, multi-stage workflow that can handle simple queries, complex data analysis, image generation, and comprehensive reporting with full memory persistence and error recovery.
