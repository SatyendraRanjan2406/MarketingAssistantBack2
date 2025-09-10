# Ad Expert API - Complete CURL Examples

## 🔐 **Authentication Required**
All endpoints require JWT authentication. Get your token from:
```bash
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "password": "your_password"
  }'
```

## 📋 **API Endpoints**

### **1. Chat Message API**
```http
POST /ad-expert/api/chat/message/
```

**Purpose**: Send a chat message to the AI assistant for Google Ads analysis

**CURL Example:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "What is my CPA trend for Google Ads customer ID 9762343117 for the last 7 days?"
  }'
```

**Response Example:**
```json
{
  "message_id": 123,
  "conversation_id": 45,
  "response": {
    "response_type": "text",
    "content": "Based on your Google Ads data for customer ID 9762343117, here's your CPA trend for the last 7 days...",
    "title": "CPA Analysis"
  },
  "timestamp": "2025-09-03T11:00:00.000000+00:00"
}
```

**Alternative Message Examples:**
```bash
# Ask about campaign performance
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Show me the performance of my top 5 campaigns by spend"
  }'

# Ask about budget optimization
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Which campaigns should I increase budget for based on ROAS?"
  }'

# Ask for specific metrics
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "What is my CTR and CPC for search campaigns vs display campaigns?"
  }'
```

---

### **2. Get Conversations API**
```http
GET /ad-expert/api/conversations/
```

**Purpose**: Retrieve all conversations for the authenticated user

**CURL Example:**
```bash
curl -X GET http://localhost:8000/ad-expert/api/conversations/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Accept: application/json"
```

**Response Example:**
```json
{
  "success": true,
  "conversations": [
    {
      "id": 45,
      "title": "CPA Analysis - Customer 9762343117",
      "created_at": "2025-09-03T10:30:00.000000+00:00",
      "updated_at": "2025-09-03T11:00:00.000000+00:00",
      "message_count": 3,
      "last_message": "What is my CPA trend for Google Ads customer ID 9762343117 for the last 7 days?"
    },
    {
      "id": 44,
      "title": "Campaign Performance Review",
      "created_at": "2025-09-03T09:15:00.000000+00:00",
      "updated_at": "2025-09-03T09:45:00.000000+00:00",
      "message_count": 5,
      "last_message": "Show me the performance of my top 5 campaigns by spend"
    }
  ]
}
```

---

### **3. Get Conversation Messages API**
```http
GET /ad-expert/api/conversations/{conversation_id}/
```

**Purpose**: Retrieve all messages in a specific conversation

**CURL Example:**
```bash
curl -X GET http://localhost:8000/ad-expert/api/conversations/45/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Accept: application/json"
```

**Response Example:**
```json
{
  "success": true,
  "conversation": {
    "id": 45,
    "title": "CPA Analysis - Customer 9762343117",
    "created_at": "2025-09-03T10:30:00.000000+00:00",
    "updated_at": "2025-09-03T11:00:00.000000+00:00"
  },
  "messages": [
    {
      "id": 123,
      "role": "user",
      "content": "What is my CPA trend for Google Ads customer ID 9762343117 for the last 7 days?",
      "created_at": "2025-09-03T10:30:00.000000+00:00"
    },
    {
      "id": 124,
      "role": "assistant",
      "content": "Based on your Google Ads data for customer ID 9762343117, here's your CPA trend for the last 7 days...",
      "response_type": "text",
      "created_at": "2025-09-03T10:30:15.000000+00:00"
    },
    {
      "id": 125,
      "role": "user",
      "content": "Can you show me a chart of this data?",
      "created_at": "2025-09-03T11:00:00.000000+00:00"
    }
  ]
}
```

---

### **4. Delete Conversation API**
```http
DELETE /ad-expert/api/conversations/{conversation_id}/delete/
```

**Purpose**: Delete a specific conversation and all its messages

**CURL Example:**
```bash
curl -X DELETE http://localhost:8000/ad-expert/api/conversations/45/delete/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Accept: application/json"
```

**Response Example:**
```json
{
  "success": true,
  "message": "Conversation deleted successfully"
}
```

---

## 🧪 **Complete Testing Workflow**

### **Step 1: Login and Get Token**
```bash
# Login to get JWT token
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePassword123!"
  }'

# Extract access_token from response and use it in subsequent requests
```

### **Step 2: Send Chat Message**
```bash
# Send a chat message
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "What is my CPA trend for Google Ads customer ID 9762343117 for the last 7 days?"
  }'
```

### **Step 3: Get All Conversations**
```bash
# Get all conversations
curl -X GET http://localhost:8000/ad-expert/api/conversations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Accept: application/json"
```

### **Step 4: Get Specific Conversation Messages**
```bash
# Get messages from a specific conversation (use conversation_id from step 2)
curl -X GET http://localhost:8000/ad-expert/api/conversations/45/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Accept: application/json"
```

### **Step 5: Delete Conversation (Optional)**
```bash
# Delete a conversation
curl -X DELETE http://localhost:8000/ad-expert/api/conversations/45/delete/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Accept: application/json"
```

---

## 🔗 **Integration with Google OAuth**

### **Prerequisites: Connect Google OAuth**
```bash
# Check Google OAuth connection status
curl -X GET http://localhost:8000/accounts/api/google-oauth/connect/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Accept: application/json"

# If not connected, follow the authorization_url to connect Google account
```

### **Chat with Google Ads Data**
```bash
# Once Google OAuth is connected, you can ask about Google Ads data
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "Analyze my Google Ads performance for customer ID 9762343117. Show me CPA trends, top performing campaigns, and budget recommendations."
  }'
```

---

## 📊 **Response Types**

The chat API can return different response types:

### **Text Response**
```json
{
  "response_type": "text",
  "content": "Your CPA has increased by 15% over the last 7 days...",
  "title": "CPA Analysis"
}
```

### **Table Response**
```json
{
  "response_type": "table",
  "title": "Campaign Performance",
  "data": [
    {"Campaign": "Search Campaign 1", "Spend": "$1,250", "CPA": "$12.50", "ROAS": "4.2"},
    {"Campaign": "Display Campaign 2", "Spend": "$890", "CPA": "$18.90", "ROAS": "2.8"}
  ]
}
```

### **Chart Response**
```json
{
  "response_type": "line_chart",
  "title": "CPA Trend (Last 7 Days)",
  "data": [
    {"date": "2025-08-27", "cpa": 12.50},
    {"date": "2025-08-28", "cpa": 13.20},
    {"date": "2025-08-29", "cpa": 14.10}
  ]
}
```

### **Action Items Response**
```json
{
  "response_type": "action_items",
  "title": "Recommended Actions",
  "data": [
    {"action": "Increase budget for Search Campaign 1 by 20%", "priority": "high"},
    {"action": "Pause underperforming keywords in Display Campaign 2", "priority": "medium"},
    {"action": "Test new ad copy for Campaign 3", "priority": "low"}
  ]
}
```

---

## ⚠️ **Error Handling**

### **Authentication Error**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

### **Google OAuth Not Connected**
```json
{
  "message_id": 123,
  "conversation_id": 45,
  "response": {
    "response_type": "text",
    "content": "Please connect your Google Ads account first to analyze campaign data.",
    "title": "Google OAuth Required"
  },
  "timestamp": "2025-09-03T11:00:00.000000+00:00"
}
```

### **Invalid Customer ID**
```json
{
  "message_id": 123,
  "conversation_id": 45,
  "response": {
    "response_type": "text",
    "content": "Customer ID 1234567890 not found or not accessible. Please check your Google Ads account permissions.",
    "title": "Customer ID Error"
  },
  "timestamp": "2025-09-03T11:00:00.000000+00:00"
}
```

---

## 🎯 **Best Practices**

1. **Always include Authorization header** with valid JWT token
2. **Use specific customer IDs** when asking about Google Ads data
3. **Be specific in your questions** for better AI responses
4. **Check Google OAuth connection** before asking for Google Ads data
5. **Handle errors gracefully** in your frontend application
6. **Store conversation IDs** for follow-up questions

---

## 🚀 **Quick Start Example**

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser@example.com", "password": "SecurePassword123!"}' | \
  jq -r '.data.tokens.access_token')

# 2. Send chat message
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "What is my CPA trend for Google Ads customer ID 9762343117 for the last 7 days?"
  }'

# 3. Get conversations
curl -X GET http://localhost:8000/ad-expert/api/conversations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"
```

**All ad_expert API endpoints are now ready for testing and integration!** 🚀


