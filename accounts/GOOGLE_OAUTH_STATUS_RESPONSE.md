# Google OAuth Status API - Response Format

## 📋 **API Endpoint**
```http
GET /accounts/api/google-oauth/status/
```

## 🔐 **Authentication Required**
- ✅ **JWT Token Required**: Must include `Authorization: Bearer YOUR_JWT_TOKEN`

## 📤 **Response Formats**

### **1. No Google OAuth Connection (Not Connected)**

**Response (200):**
```json
{
  "success": true,
  "connected": false,
  "message": "No active Google OAuth connection"
}
```

**When this occurs:**
- User has never connected their Google account
- User disconnected their Google account
- Google OAuth connection is inactive/expired

### **2. Active Google OAuth Connection (Connected)**

**Response (200):**
```json
{
  "success": true,
  "connected": true,
  "google_auth": {
    "id": 1,
    "google_email": "user@gmail.com",
    "google_name": "John Doe",
    "scopes": "https://www.googleapis.com/auth/userinfo.profile,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/analytics.readonly",
    "is_active": true,
    "last_used": "2025-01-27T12:00:00Z",
    "token_expiry": "2025-01-27T13:00:00Z"
  }
}
```

**Field Descriptions:**
- **`id`**: Database ID of the Google OAuth connection
- **`google_email`**: User's Google account email
- **`google_name`**: User's Google account display name
- **`scopes`**: Comma-separated list of granted OAuth scopes
- **`is_active`**: Whether the OAuth connection is active
- **`last_used`**: Last time the OAuth connection was used (ISO format)
- **`token_expiry`**: When the access token expires (ISO format)

## 🧪 **Test Examples**

### **Test 1: Check OAuth Status (Not Connected)**
```bash
curl 'http://localhost:8000/accounts/api/google-oauth/status/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Accept: application/json'
```

**Response:**
```json
{
  "success": true,
  "connected": false,
  "message": "No active Google OAuth connection"
}
```

### **Test 2: Check OAuth Status (Connected)**
```bash
curl 'http://localhost:8000/accounts/api/google-oauth/status/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Accept: application/json'
```

**Response:**
```json
{
  "success": true,
  "connected": true,
  "google_auth": {
    "id": 1,
    "google_email": "user@gmail.com",
    "google_name": "John Doe",
    "scopes": "https://www.googleapis.com/auth/userinfo.profile,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/analytics.readonly",
    "is_active": true,
    "last_used": "2025-01-27T12:00:00Z",
    "token_expiry": "2025-01-27T13:00:00Z"
  }
}
```

## 🔍 **Response Analysis**

### **Your Actual Response:**
```json
{
  "success": true,
  "connected": false,
  "message": "No active Google OAuth connection"
}
```

**This means:**
- ✅ **API is working correctly**
- ❌ **No Google OAuth connection found for this user**
- 🔗 **User needs to connect their Google account first**

## 🔄 **Next Steps Based on Response**

### **If `connected: false`:**
1. **Initiate OAuth Flow:**
   ```bash
   curl -X GET http://localhost:8000/accounts/api/google-oauth/initiate/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

2. **User visits authorization URL** to grant permissions

3. **Exchange authorization code** for tokens

4. **Check status again** to confirm connection

### **If `connected: true`:**
1. **Use Google Ads API** with the connected account
2. **Check token expiry** and refresh if needed
3. **Access Google Ads data** through ad_expert API

## 🛠️ **Frontend Integration**

### **JavaScript Example:**
```javascript
async function checkGoogleOAuthStatus() {
  try {
    const response = await fetch('/accounts/api/google-oauth/status/', {
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Accept': 'application/json'
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      if (data.connected) {
        console.log('Google OAuth connected:', data.google_auth);
        // User can access Google Ads features
      } else {
        console.log('Google OAuth not connected:', data.message);
        // Show "Connect Google Account" button
      }
    }
  } catch (error) {
    console.error('Error checking OAuth status:', error);
  }
}
```

### **React Component Example:**
```jsx
import { useState, useEffect } from 'react';

function GoogleOAuthStatus() {
  const [oauthStatus, setOauthStatus] = useState(null);
  
  useEffect(() => {
    checkOAuthStatus();
  }, []);
  
  const checkOAuthStatus = async () => {
    const response = await fetch('/accounts/api/google-oauth/status/', {
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Accept': 'application/json'
      }
    });
    
    const data = await response.json();
    setOauthStatus(data);
  };
  
  return (
    <div>
      {oauthStatus?.connected ? (
        <div>
          <h3>Google Account Connected</h3>
          <p>Email: {oauthStatus.google_auth.google_email}</p>
          <p>Name: {oauthStatus.google_auth.google_name}</p>
        </div>
      ) : (
        <div>
          <h3>Connect Google Account</h3>
          <p>{oauthStatus?.message}</p>
          <button onClick={initiateOAuth}>Connect Google</button>
        </div>
      )}
    </div>
  );
}
```

## 🔗 **Integration with ad_expert API**

### **Check OAuth Status Before Using ad_expert:**
```bash
# 1. Check if Google OAuth is connected
curl -X GET http://localhost:8000/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. If connected, use ad_expert API
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for Google Ads?"
  }'
```

## ⚠️ **Error Handling**

### **Invalid JWT Token (401):**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

### **Missing Authorization Header (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## 📝 **Summary**

The Google OAuth Status API returns:

- ✅ **`success: true`** - API call successful
- ✅ **`connected: false`** - No Google OAuth connection (your case)
- ✅ **`message`** - Human-readable status message
- ✅ **`google_auth`** - OAuth connection details (when connected)

**Your response indicates:** The user needs to connect their Google account first before using Google Ads features! 🔗

