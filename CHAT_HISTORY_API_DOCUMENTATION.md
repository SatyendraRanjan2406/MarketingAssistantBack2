# Chat History API Documentation

## 🔐 **Authentication Required**
All endpoints require authentication. Use JWT token or session authentication.

## 📡 **API Endpoints**

### **Get Chat Messages for Conversation**
```
GET /ad-expert/api/conversations/{conversation_id}/messages/
```

#### **Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Messages per page (default: 50, max: 100)
- `order` (optional): Message order - `asc` (oldest first) or `desc` (newest first, default)

#### **Response Format:**
```json
{
    "success": true,
    "conversation_id": 123,
    "conversation_title": "Campaign Analysis",
    "messages": [
        {
            "id": 1,
            "role": "user",
            "content": "Show me my campaigns",
            "response_type": "text",
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
            "structured_data": null
        },
        {
            "id": 2,
            "role": "assistant",
            "content": "Here are your campaigns...",
            "response_type": "text",
            "created_at": "2024-01-01T10:00:05Z",
            "updated_at": "2024-01-01T10:00:05Z",
            "structured_data": {
                "tools_used": ["get_campaigns"],
                "customer_id": "customers/1234567890"
            }
        }
    ],
    "pagination": {
        "current_page": 1,
        "page_size": 50,
        "total_messages": 150,
        "total_pages": 3,
        "has_next": true,
        "has_previous": false,
        "next_page": 2,
        "previous_page": null
    }
}
```

## 🔒 **Security Features**

### **User Isolation**
- Users can only access their own conversations
- 404 error returned for conversations not owned by the user
- No data leakage between users

### **Input Validation**
- Page numbers must be positive integers
- Page size limited to maximum 100 messages
- Invalid parameters return 400 Bad Request

## 📝 **cURL Examples**

### **1. Get Latest Messages (Default)**
```bash
curl -X GET "http://localhost:8000/ad-expert/api/conversations/123/messages/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### **2. Get Messages with Pagination**
```bash
curl -X GET "http://localhost:8000/ad-expert/api/conversations/123/messages/?page=2&page_size=25" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### **3. Get Messages in Chronological Order (Oldest First)**
```bash
curl -X GET "http://localhost:8000/ad-expert/api/conversations/123/messages/?order=asc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### **4. Get Maximum Messages per Page**
```bash
curl -X GET "http://localhost:8000/ad-expert/api/conversations/123/messages/?page_size=100" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

## 🚨 **Error Responses**

### **404 - Conversation Not Found**
```json
{
    "success": false,
    "error": "Conversation not found or access denied",
    "conversation_id": 123
}
```

### **400 - Invalid Parameters**
```json
{
    "success": false,
    "error": "Invalid pagination parameters",
    "details": "invalid literal for int() with base 10: 'invalid'"
}
```

### **401 - Unauthorized**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### **500 - Server Error**
```json
{
    "success": false,
    "error": "Failed to retrieve chat history",
    "details": "Database connection error"
}
```

## 🎯 **Use Cases**

### **Chat Bot Frontend**
- Load conversation history when opening a chat
- Implement infinite scroll with pagination
- Show message timestamps and metadata

### **Analytics Dashboard**
- Analyze conversation patterns
- Track user engagement
- Monitor response quality

### **Debugging & Support**
- Review user interactions
- Troubleshoot conversation issues
- Audit chat logs

## 📊 **Performance Considerations**

- **Pagination**: Default 50 messages per page, max 100
- **Indexing**: Messages indexed by conversation and created_at
- **Caching**: Consider Redis caching for frequently accessed conversations
- **Rate Limiting**: Implement rate limiting for production use

## 🔧 **Implementation Details**

### **Database Queries**
- Uses Django ORM with efficient pagination
- Filters by conversation and user ownership
- Orders by created_at timestamp

### **Security**
- JWT or session authentication required
- User ownership verification
- Input validation and sanitization

### **Logging**
- All API calls logged with user and conversation info
- Error logging for debugging
- Performance metrics tracking
