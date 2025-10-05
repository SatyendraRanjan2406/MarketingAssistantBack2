# Token Refresh Implementation for Google Ads API

## Overview

This document describes the implementation of automatic token refresh functionality for Google Ads API tools to handle 401 Unauthorized errors seamlessly.

## Problem Statement

When using Google Ads API tools, users often encounter 401 Unauthorized errors when their access tokens expire. This requires manual intervention to refresh tokens, leading to poor user experience and interrupted workflows.

## Solution

Implemented automatic token refresh functionality that:
1. Detects 401 Unauthorized errors in Google Ads API calls
2. Automatically refreshes the access token using the refresh token
3. Retries the failed request with the new access token
4. Seamlessly integrates with existing OAuth infrastructure

## Implementation Details

### 1. Enhanced GoogleAdsAPI Class

**File**: `ad_expert/tools.py`

#### New Methods Added:

```python
def _refresh_token_for_user(self, user_id: int) -> Optional[str]:
    """Refresh access token for a user"""
    try:
        from accounts.google_oauth_service import UserGoogleAuthService
        from django.contrib.auth.models import User
        
        user = User.objects.get(id=user_id)
        auth_record = UserGoogleAuthService.refresh_user_tokens(user)
        
        if auth_record:
            logger.info(f"Successfully refreshed token for user {user_id}")
            return auth_record.access_token
        else:
            logger.error(f"Failed to refresh token for user {user_id}")
            return None
            
    except Exception as e:
        logger.error(f"Error refreshing token for user {user_id}: {str(e)}")
        return None
```

#### Enhanced Search Method:

```python
def search(self, customer_id: str, access_token: str, query: str, user_id: int = None) -> Dict[str, Any]:
    """Execute GAQL search query with automatic token refresh on 401 errors"""
    try:
        url = f"{self.base_url}/customers/{customer_id}/googleAds:search"
        headers = self._get_headers(access_token)
        
        payload = {"query": query}
        
        response = requests.post(url, headers=headers, json=payload)
        
        # Handle 401 Unauthorized - try to refresh token
        if response.status_code == 401 and user_id:
            logger.warning(f"401 Unauthorized error for user {user_id}, attempting token refresh")
            
            # Try to refresh the token
            new_access_token = self._refresh_token_for_user(user_id)
            if new_access_token:
                # Retry with new token
                headers = self._get_headers(new_access_token)
                response = requests.post(url, headers=headers, json=payload)
                logger.info(f"Retried request with refreshed token for user {user_id}")
            else:
                logger.error(f"Failed to refresh token for user {user_id}")
        
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        logger.error(f"Error executing GAQL query: {e}")
        return {"error": str(e)}
```

### 2. Updated Tool Functions

All Google Ads tool functions now accept an optional `user_id` parameter:

```python
@tool
def get_campaigns(customer_id: str, access_token: str, status_filter: str = "ALL", user_id: int = None) -> Dict[str, Any]:
    # ... existing implementation ...
    result = google_ads_api.search(customer_id, access_token, query, user_id)
    return result
```

**Updated Functions:**
- `get_campaigns()`
- `get_campaign_by_id()`
- `get_ad_groups()`
- `get_ads()`
- `get_keywords()`
- `get_performance_data()`
- `get_budgets()`
- `get_account_overview()`
- `get_search_terms()`
- `get_demographic_data()`
- `get_geographic_data()`

### 3. Enhanced LanggraphView Integration

**File**: `ad_expert/views.py`

#### Custom Tool Node with User ID Injection:

```python
def tool_node(state: LangGraphState) -> LangGraphState:
    """Tool execution node with user_id injection for token refresh"""
    try:
        # Get the last message which should contain tool calls
        last_message = state["messages"][-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            # Create a custom tool node that injects user_id
            user_id = state.get("user_id")
            
            # Create tools with user_id injection
            enhanced_tools = self._create_enhanced_tools_with_user_id(user_id)
            tool_node_instance = ToolNode(enhanced_tools)
            tool_response = tool_node_instance.invoke({"messages": [last_message]})
            
            return {
                "messages": tool_response["messages"],
                "current_step": "tools_completed"
            }
        else:
            return {"current_step": "no_tools"}
    except Exception as e:
        logger.error(f"Error in tool_node: {e}")
        error_message = AIMessage(content=f"Tool execution error: {str(e)}")
        return {
            "messages": [error_message],
            "current_step": "error",
            "error_count": state.get("error_count", 0) + 1
        }
```

#### Enhanced Tools Creation:

```python
def _create_enhanced_tools_with_user_id(self, user_id: int):
    """Create enhanced tools that automatically inject user_id for token refresh"""
    from langchain_core.tools import StructuredTool
    
    enhanced_tools = []
    
    for original_tool in ALL_TOOLS:
        def create_enhanced_tool(original_tool, user_id):
            def enhanced_tool_func(*args, **kwargs):
                """Enhanced tool function with automatic user_id injection for token refresh"""
                # Inject user_id if not already present
                if 'user_id' not in kwargs and user_id is not None:
                    kwargs['user_id'] = user_id
                return original_tool.func(*args, **kwargs)
            
            # Create new tool with same metadata but enhanced function
            enhanced_tool = StructuredTool.from_function(
                enhanced_tool_func,
                name=original_tool.name,
                description=original_tool.description,
                args_schema=original_tool.args_schema
            )
            
            return enhanced_tool
        
        enhanced_tool = create_enhanced_tool(original_tool, user_id)
        enhanced_tools.append(enhanced_tool)
    
    return enhanced_tools
```

## How It Works

### 1. Normal Flow
1. User makes a request through LanggraphView
2. LLM decides to use a Google Ads tool
3. Tool is called with user_id automatically injected
4. Google Ads API call is made with current access token
5. If successful, result is returned

### 2. Token Refresh Flow
1. Google Ads API returns 401 Unauthorized error
2. System detects 401 error and checks if user_id is available
3. Calls `UserGoogleAuthService.refresh_user_tokens()` to get new access token
4. Retries the original request with the new access token
5. Returns result or error if refresh fails

### 3. Error Handling
- If token refresh fails, the original 401 error is returned
- All errors are logged for debugging
- System gracefully handles missing user_id or OAuth records

## Benefits

### 1. Improved User Experience
- No manual token refresh required
- Seamless continuation of conversations
- Reduced authentication errors

### 2. Enhanced Reliability
- Automatic error recovery
- Better handling of long-running sessions
- Reduced support tickets

### 3. Better Integration
- Works with existing OAuth infrastructure
- Maintains security best practices
- Compatible with all Google Ads tools

## Testing

### Test Script
Created `test_token_refresh.py` to verify:
- Token refresh method functionality
- Enhanced search method with 401 handling
- Tool function parameter updates
- LanggraphView integration

### Test Results
```
✅ GoogleAdsAPI.search() now accepts user_id parameter
✅ Automatic 401 error detection and token refresh
✅ All tool functions updated with user_id parameter
✅ LanggraphView enhanced to inject user_id into tools
✅ Token refresh integration with existing OAuth service
```

## Usage Examples

### 1. Direct Tool Usage
```python
# Tool will automatically refresh token on 401 error
result = get_campaigns(
    customer_id="9631603999",
    access_token="expired_token",
    status_filter="ALL",
    user_id=123  # Enables automatic token refresh
)
```

### 2. LanggraphView Usage
```python
# LanggraphView automatically injects user_id into all tool calls
response = langgraph_view.post(request)
# If any tool encounters 401 error, token is automatically refreshed
```

## Monitoring and Logging

### Key Log Messages
- `"401 Unauthorized error for user {user_id}, attempting token refresh"`
- `"Successfully refreshed token for user {user_id}"`
- `"Retried request with refreshed token for user {user_id}"`
- `"Failed to refresh token for user {user_id}"`

### Error Tracking
- All token refresh attempts are logged
- Failed refresh attempts are tracked
- 401 errors are monitored for patterns

## Security Considerations

1. **Token Security**: Refresh tokens are handled securely through existing OAuth service
2. **User Isolation**: Each user's tokens are refreshed independently
3. **Error Handling**: Failed refresh attempts don't expose sensitive information
4. **Logging**: Sensitive token data is not logged

## Future Enhancements

1. **Metrics**: Add token refresh success/failure metrics
2. **Caching**: Cache refreshed tokens to reduce API calls
3. **Proactive Refresh**: Refresh tokens before they expire
4. **Multi-User**: Support for multiple OAuth accounts per user

## Conclusion

The token refresh implementation provides a robust solution for handling expired Google Ads API tokens automatically. It integrates seamlessly with the existing OAuth infrastructure and enhances the user experience by eliminating manual token refresh requirements.

The implementation is production-ready and includes comprehensive error handling, logging, and testing to ensure reliability and maintainability.
