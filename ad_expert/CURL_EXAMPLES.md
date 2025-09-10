# Ad Expert API - Complete CURL Examples

## 🔐 **Authentication Flow**

### Step 1: Login to Get JWT Token

```bash
curl -X POST http://localhost:8000/api-auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**Expected Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1NzQ4ODc5NSwiaWF0IjoxNzU2ODgzNzk1LCJqdGkiOiJhYjdkMTJiNWU2YTA0NWFkOTk2MTJiYjcwOTJmNDJlYSIsInVzZXJfaWQiOjJ9.example_refresh_token"
}
```

### Step 2: Test Authentication

```bash
curl -X GET http://localhost:8000/ad-expert/api/test-auth/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "message": "Authentication successful",
  "user_id": 2,
  "username": "your_username",
  "is_authenticated": true,
  "timestamp": "2025-01-27T12:00:00.123456Z"
}
```

---

## 💬 **Chat Message Endpoints**

### Basic Chat Message

```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me analyze my Google Ads performance?"
  }'
```

**Expected Response:**
```json
{
  "message_id": 1,
  "conversation_id": 1,
  "response": {
    "response_type": "text",
    "title": "Welcome to Ad Expert",
    "content": "Hello! I'm your AI advertising co-pilot. I can help you analyze your Google Ads and Meta Marketing campaigns. To get started, I'll need you to connect your accounts first.\n\nI can help you with:\n• Campaign performance analysis\n• CPA and ROI trends\n• Budget optimization recommendations\n• Cross-platform comparisons\n• Actionable insights and next steps\n\nWould you like to connect your Google Ads or Meta account to begin?",
    "data": [],
    "insights": [
      "Connect your Google Ads account for search campaign analysis",
      "Connect your Meta account for social media campaign insights"
    ]
  },
  "timestamp": "2025-01-27T12:00:00.123456Z"
}
```

### Chat Message with Conversation ID

```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for the last 14 days?",
    "conversation_id": 1
  }'
```

**Expected Response (with Google Ads connected):**
```json
{
  "message_id": 2,
  "conversation_id": 1,
  "response": {
    "response_type": "line_chart",
    "title": "CPA Trend - Last 14 Days",
    "content": "Your CPA has been trending downward over the past 14 days, showing a 12% improvement. Here's the detailed breakdown:",
    "data": [
      {
        "label": "2025-01-14",
        "value": 45.20,
        "description": "CPA: $45.20, Spend: $2,250"
      },
      {
        "label": "2025-01-15",
        "value": 43.80,
        "description": "CPA: $43.80, Spend: $2,190"
      }
    ],
    "insights": [
      "CPA decreased by 12% over 14 days",
      "Best performing day: Jan 27 with $32.50 CPA",
      "Consistent downward trend indicates optimization success"
    ]
  },
  "timestamp": "2025-01-27T12:05:00.123456Z"
}
```

### Chat Message Requesting Campaign Comparison

```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me a comparison of my top 5 campaigns by spend",
    "conversation_id": 1
  }'
```

**Expected Response:**
```json
{
  "message_id": 3,
  "conversation_id": 1,
  "response": {
    "response_type": "table",
    "title": "Top 5 Campaigns by Spend",
    "content": "Here's a detailed comparison of your top 5 campaigns ranked by spend:",
    "data": [
      {
        "label": "Campaign Name",
        "value": "Performance Metrics",
        "description": "Search - Brand Keywords"
      },
      {
        "label": "Spend",
        "value": 12500.00,
        "description": "$12,500"
      },
      {
        "label": "CTR",
        "value": 4.0,
        "description": "4.0%"
      }
    ],
    "insights": [
      "Brand Keywords campaign has highest spend but good CTR",
      "CPA is above average - consider optimizing landing pages"
    ]
  },
  "timestamp": "2025-01-27T12:10:00.123456Z"
}
```

---

## 📋 **Additional Endpoints**

### Get Conversations

```bash
curl -X GET http://localhost:8000/ad-expert/api/conversations/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "title": "Chat 2025-01-27 12:00",
    "created_at": "2025-01-27T12:00:00.123456Z",
    "updated_at": "2025-01-27T12:10:00.123456Z",
    "message_count": 3
  }
]
```

### Get Conversation Messages

```bash
curl -X GET http://localhost:8000/ad-expert/api/conversations/1/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g"
```

### Get OAuth Connections

```bash
curl -X GET http://localhost:8000/ad-expert/api/oauth/connections/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "platform": "google",
    "account_id": "123-456-7890",
    "email": "user@gmail.com",
    "name": "User Name",
    "created_at": "2025-01-27T10:00:00.123456Z",
    "is_token_valid": true
  }
]
```

### Health Check

```bash
curl -X GET http://localhost:8000/ad-expert/api/health/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T12:00:00.123456Z",
  "user": "your_username"
}
```

---

## 🔧 **Complete Working Example**

### Step-by-Step Flow:

1. **Login and get token:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api-auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}' | \
  jq -r '.access')

echo "Token: $TOKEN"
```

2. **Test authentication:**
```bash
curl -X GET http://localhost:8000/ad-expert/api/test-auth/ \
  -H "Authorization: Bearer $TOKEN"
```

3. **Send chat message:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me analyze my Google Ads performance?"
  }'
```

4. **Continue conversation:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for the last 14 days?",
    "conversation_id": 1
  }'
```

---

## ⚠️ **Error Responses**

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 400 Bad Request
```json
{
  "error": "Message is required"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## 📝 **Notes**

- **Replace `your_username` and `your_password`** with actual credentials
- **Replace the JWT token** with the actual token from login response
- **All timestamps** are in ISO 8601 format
- **Conversation ID** is optional - if not provided, a new conversation is created
- **Response formats** vary based on query type (text, charts, tables, action items)
- **OAuth connections** are now managed through the centralized accounts app

The API is fully functional and ready for React frontend integration!

