# 🔑 Token Authentication Guide

## **Overview**

Your system uses two types of tokens:
1. **JWT Token** - For API authentication (Django)
2. **Google OAuth Token** - For Google Ads API access

---

## **1. JWT Token (Django API Authentication)**

### **Get JWT Token:**
```bash
curl -X POST 'http://localhost:8000/accounts/api/auth/login/' \
  -H 'Content-Type: application/json' \
  -d '{"email": "your_email@example.com", "password": "your_password"}'
```

**Response:**
```json
{
  "success": true,
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "your_email@example.com"
  }
}
```

### **Use JWT Token:**
```bash
# Set your token as a variable
export JWT_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Use in API calls
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/api/query/' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"query": "How do I create a campaign?"}'
```

---

## **2. Google OAuth Token (Google Ads API)**

### **Step 1: Initiate OAuth Flow**
```bash
curl -X GET 'http://localhost:8000/accounts/api/google-oauth/initiate/'
```

**Response:**
```json
{
  "success": true,
  "auth_url": "https://accounts.google.com/oauth/authorize?client_id=...",
  "state": "random_state_string"
}
```

### **Step 2: Complete OAuth in Browser**
1. Copy the `auth_url` from the response
2. Open it in your browser
3. Login with your Google account
4. Grant permissions for Google Ads API
5. You'll be redirected to the callback URL

### **Step 3: Check OAuth Status**
```bash
curl -X GET 'http://localhost:8000/accounts/api/google-oauth/status/' \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "is_connected": true,
  "user_info": {
    "email": "your_email@gmail.com",
    "name": "Your Name"
  },
  "google_ads_access": true,
  "accessible_customers": [
    "customers/1234567890",
    "customers/0987654321"
  ]
}
```

---

## **3. Complete Workflow Example**

### **Step 1: Get JWT Token**
```bash
# Login to get JWT token
JWT_RESPONSE=$(curl -s -X POST 'http://localhost:8000/accounts/api/auth/login/' \
  -H 'Content-Type: application/json' \
  -d '{"email": "your_email@example.com", "password": "your_password"}')

# Extract JWT token
JWT_TOKEN=$(echo $JWT_RESPONSE | jq -r '.access')
echo "JWT Token: $JWT_TOKEN"
```

### **Step 2: Check Google OAuth Status**
```bash
# Check if Google OAuth is connected
curl -X GET 'http://localhost:8000/accounts/api/google-oauth/status/' \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### **Step 3: Use RAG APIs**

#### **Documentation-only RAG:**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/api/query/' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"query": "How do I create a campaign?"}'
```

#### **Hybrid RAG (with live data):**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/api/hybrid/' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"query": "Show me my campaigns", "customer_id": "1234567890"}'
```

---

## **4. Quick Test Script**

```bash
#!/bin/bash

# Set your credentials
EMAIL="your_email@example.com"
PASSWORD="your_password"
CUSTOMER_ID="1234567890"

# Get JWT token
echo "🔑 Getting JWT token..."
JWT_RESPONSE=$(curl -s -X POST 'http://localhost:8000/accounts/api/auth/login/' \
  -H 'Content-Type: application/json' \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

JWT_TOKEN=$(echo $JWT_RESPONSE | jq -r '.access')

if [ "$JWT_TOKEN" = "null" ]; then
  echo "❌ Failed to get JWT token"
  echo $JWT_RESPONSE
  exit 1
fi

echo "✅ JWT token obtained"

# Test regular RAG
echo "🤖 Testing regular RAG..."
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/api/query/' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"query": "How do I create a campaign?"}' | jq

# Test hybrid RAG
echo "🔗 Testing hybrid RAG..."
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/api/hybrid/' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d "{\"query\": \"Show me my campaigns\", \"customer_id\": \"$CUSTOMER_ID\"}" | jq
```

---

## **5. Troubleshooting**

### **JWT Token Issues:**
- Make sure you're using the correct email/password
- Check if the user account exists
- Verify the login endpoint is working

### **Google OAuth Issues:**
- Make sure Google OAuth is properly configured
- Check environment variables (GOOGLE_OAUTH_CLIENT_ID, etc.)
- Verify the redirect URI matches your setup

### **API Call Issues:**
- Make sure Django server is running on port 8000
- Check if the JWT token is valid and not expired
- Verify the customer ID format (should be like "1234567890")

---

## **6. Environment Variables Needed**

```bash
# Django JWT
SECRET_KEY="your-secret-key"
SIMPLE_JWT_SECRET_KEY="your-jwt-secret"

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID="your-client-id"
GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"
GOOGLE_OAUTH_REDIRECT_URI="http://localhost:8000/accounts/api/google-oauth/callback/"

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN="your-developer-token"
GOOGLE_ADS_CLIENT_ID="your-ads-client-id"
GOOGLE_ADS_CLIENT_SECRET="your-ads-client-secret"
```

---

## **7. Summary**

1. **JWT Token** = Access to your Django API
2. **Google OAuth** = Access to Google Ads API
3. **Both needed** for hybrid RAG with live data
4. **JWT only** for documentation-only RAG

The system is designed to be secure and requires proper authentication for both the Django API and Google Ads API access.

