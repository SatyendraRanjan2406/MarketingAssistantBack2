# Google OAuth Connect API - Complete Token Management

## 🎯 **New API Endpoint**
```http
GET /accounts/api/google-oauth/connect/
```

## 🔐 **Authentication Required**
- ✅ **JWT Token Required**: Must include `Authorization: Bearer YOUR_JWT_TOKEN`

## 🚀 **What This API Does**

This new API provides **complete Google OAuth token management** in a single call:

1. **Checks existing Google OAuth connection** for the user
2. **Validates token expiry** and refreshes if needed
3. **Returns connection status** with detailed token information
4. **Handles all token lifecycle** automatically

## 📤 **Response Formats**

### **1. Valid Connection (Token Active)**

**Response (200):**
```json
{
  "success": true,
  "connected": true,
  "message": "Google OAuth connection is active and valid",
  "google_auth": {
    "id": 2,
    "google_email": "kstarbootcamp@gmail.com",
    "google_name": "KSTAR TECH",
    "scopes": "https://www.googleapis.com/auth/adwords https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid",
    "is_active": true,
    "last_used": "2025-09-03T09:07:10.627248+00:00Z",
    "token_expiry": "2025-09-03T10:07:09.379295+00:00Z",
    "is_token_expired": false,
    "needs_refresh": false
  }
}
```

### **2. Token Refreshed Successfully**

**Response (200):**
```json
{
  "success": true,
  "connected": true,
  "message": "Google OAuth connection refreshed successfully",
  "google_auth": {
    "id": 2,
    "google_email": "kstarbootcamp@gmail.com",
    "google_name": "KSTAR TECH",
    "scopes": "https://www.googleapis.com/auth/adwords https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid",
    "is_active": true,
    "last_used": "2025-09-03T09:15:00.000000+00:00Z",
    "token_expiry": "2025-09-03T10:15:00.000000+00:00Z",
    "is_token_expired": false,
    "needs_refresh": false
  }
}
```

### **3. No Google OAuth Connection**

**Response (401):**
```json
{
  "success": false,
  "connected": false,
  "message": "No Google OAuth connection found. Please initiate OAuth flow first.",
  "requires_reauth": true
}
```

### **4. Token Refresh Failed**

**Response (401):**
```json
{
  "success": false,
  "connected": false,
  "error": "Google OAuth token refresh failed. Please reconnect your Google account.",
  "requires_reauth": true
}
```

### **5. Server Error**

**Response (500):**
```json
{
  "success": false,
  "connected": false,
  "error": "Error message describing what went wrong",
  "requires_reauth": true
}
```

## 🧪 **Test Examples**

### **Test 1: Check Connection Status**
```bash
curl 'http://localhost:8000/accounts/api/google-oauth/connect/' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Origin: http://localhost:5173' \
  -H 'Referer: http://localhost:5173/'
```

### **Test 2: Production URL**
```bash
curl 'https://your-api-domain.com/accounts/api/google-oauth/connect/' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive'
```

## 🔄 **API Logic Flow**

### **Step 1: Check Existing Connection**
```python
auth_record = auth_service.get_valid_auth(request.user)
```

### **Step 2: Token Validation**
```python
if auth_record:
    if auth_record.is_token_expired():
        # Try to refresh token
        refreshed_record = auth_service.refresh_user_tokens(request.user)
        if refreshed_record:
            # Return refreshed token info
        else:
            # Return 401 - requires reauth
    else:
        # Token is valid, return current info
else:
    # No connection found, return 401
```

### **Step 3: Response Generation**
- **200**: Valid connection (active or refreshed)
- **401**: No connection or refresh failed
- **500**: Server error

## 🎯 **Use Cases**

### **1. Frontend Connection Check**
```javascript
async function checkGoogleConnection() {
  try {
    const response = await fetch('/accounts/api/google-oauth/connect/', {
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Accept': 'application/json'
      }
    });
    
    const data = await response.json();
    
    if (response.status === 200 && data.connected) {
      console.log('Google OAuth connected:', data.google_auth);
      // User can access Google Ads features
      return true;
    } else if (response.status === 401) {
      console.log('Google OAuth not connected or expired');
      // Show "Connect Google Account" button
      return false;
    }
  } catch (error) {
    console.error('Error checking Google connection:', error);
    return false;
  }
}
```

### **2. Before Using ad_expert API**
```javascript
async function useAdExpertAPI() {
  // First check Google OAuth connection
  const isConnected = await checkGoogleConnection();
  
  if (isConnected) {
    // Use ad_expert API
    const response = await fetch('/ad-expert/api/chat/message/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: "What is my CPA trend for Google Ads?"
      })
    });
    
    return await response.json();
  } else {
    throw new Error('Google OAuth connection required');
  }
}
```

### **3. React Component Integration**
```jsx
import { useState, useEffect } from 'react';

function GoogleConnectionStatus() {
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    checkConnection();
  }, []);
  
  const checkConnection = async () => {
    try {
      const response = await fetch('/accounts/api/google-oauth/connect/', {
        headers: {
          'Authorization': `Bearer ${jwtToken}`,
          'Accept': 'application/json'
        }
      });
      
      const data = await response.json();
      setConnectionStatus(data);
    } catch (error) {
      console.error('Error checking connection:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Checking Google connection...</div>;
  
  return (
    <div>
      {connectionStatus?.connected ? (
        <div className="connected">
          <h3>✅ Google Account Connected</h3>
          <p>Email: {connectionStatus.google_auth.google_email}</p>
          <p>Name: {connectionStatus.google_auth.google_name}</p>
          <p>Token Expiry: {new Date(connectionStatus.google_auth.token_expiry).toLocaleString()}</p>
          <p>Status: {connectionStatus.message}</p>
        </div>
      ) : (
        <div className="not-connected">
          <h3>❌ Google Account Not Connected</h3>
          <p>{connectionStatus?.message || 'Please connect your Google account'}</p>
          <button onClick={initiateOAuth}>Connect Google Account</button>
        </div>
      )}
    </div>
  );
}
```

## 🔒 **Security Features**

### **1. JWT Authentication**
- Requires valid JWT token
- Links OAuth check to authenticated user

### **2. Token Validation**
- Checks token expiry automatically
- Refreshes tokens when needed

### **3. Error Handling**
- Secure error messages
- Proper HTTP status codes
- CORS headers included

### **4. Token Lifecycle Management**
- Automatic refresh when possible
- Clear indication when reauth is needed

## 📊 **Response Field Descriptions**

### **Success Response Fields:**
- **`success`**: Boolean indicating API call success
- **`connected`**: Boolean indicating OAuth connection status
- **`message`**: Human-readable status message
- **`google_auth`**: OAuth connection details
  - **`id`**: Database ID of the connection
  - **`google_email`**: User's Google account email
  - **`google_name`**: User's Google account display name
  - **`scopes`**: Granted OAuth permissions
  - **`is_active`**: Connection status
  - **`last_used`**: Last usage timestamp (ISO format)
  - **`token_expiry`**: Token expiration time (ISO format)
  - **`is_token_expired`**: Boolean indicating if token is expired
  - **`needs_refresh`**: Boolean indicating if token needs refresh

### **Error Response Fields:**
- **`success`**: Boolean indicating API call failure
- **`connected`**: Boolean indicating no connection
- **`error`**: Error message describing the issue
- **`requires_reauth`**: Boolean indicating reauthentication needed

## 🔗 **Integration with Other APIs**

### **1. Use with ad_expert API**
```bash
# Check Google OAuth connection first
curl -X GET http://localhost:8000/accounts/api/google-oauth/connect/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# If connected, use ad_expert API
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for Google Ads customer ID 9762343117?"
  }'
```

### **2. Use with Google Ads Accounts API**
```bash
# Check connection first
curl -X GET http://localhost:8000/accounts/api/google-oauth/connect/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# If connected, get Google Ads accounts
curl -X GET http://localhost:8000/accounts/api/google-oauth/ads-accounts/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## ⚠️ **Important Notes**

1. **JWT Token Required**: API requires valid JWT authentication
2. **Automatic Token Refresh**: Tokens are refreshed automatically when possible
3. **401 Status**: Indicates reauthentication is required
4. **CORS Enabled**: Headers set for cross-origin requests
5. **Error Handling**: Comprehensive error handling with proper status codes

## 🎯 **Summary**

The new `/api/google-oauth/connect/` API provides:

- ✅ **Complete token management** in a single call
- ✅ **Automatic token refresh** when needed
- ✅ **Clear connection status** with detailed information
- ✅ **Proper error handling** with HTTP status codes
- ✅ **Frontend-friendly responses** with boolean flags
- ✅ **Security features** with JWT authentication
- ✅ **CORS support** for cross-origin requests

**Perfect for frontend applications that need to check Google OAuth connection status before using Google Ads features!** 🚀

