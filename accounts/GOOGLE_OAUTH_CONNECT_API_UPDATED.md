# Google OAuth Connect API - Complete OAuth Flow Management

## 🎯 **Updated API Endpoint**
```http
GET /accounts/api/google-oauth/connect/
```

## 🔐 **Authentication Required**
- ✅ **JWT Token Required**: Must include `Authorization: Bearer YOUR_JWT_TOKEN`

## 🚀 **What This API Does**

This API now provides **complete Google OAuth flow management** in a single call:

1. **Checks existing Google OAuth connection** for the user
2. **Validates token expiry** and refreshes if needed
3. **Initiates new OAuth flow** when no connection exists
4. **Returns appropriate response** based on connection status

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

### **3. No Google OAuth Connection - OAuth Flow Initiated**

**Response (200):**
```json
{
  "success": true,
  "connected": false,
  "message": "No Google OAuth connection found. OAuth flow initiated.",
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=540269126851-qnqiirsa85q41unhsg95qjk1aud3oihe.apps.googleusercontent.com&redirect_uri=http%3A//localhost%3A5173/google-oauth/callback/&scope=https%3A//www.googleapis.com/auth/userinfo.profile%20https%3A//www.googleapis.com/auth/userinfo.email%20https%3A//www.googleapis.com/auth/adwords%20https%3A//www.googleapis.com/auth/analytics.readonly&response_type=code&state=Fvy_Ooa6Q290wgA2eR8F7stzDUz2cGOr4YVY9FyE450&access_type=offline&prompt=consent",
  "state": "Fvy_Ooa6Q290wgA2eR8F7stzDUz2cGOr4YVY9FyE450",
  "requires_reauth": false
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

### **Test 1: First-Time User (No Google OAuth)**
```bash
curl --location 'http://localhost:8000/accounts/api/google-oauth/connect/' \
--header 'Authorization: Bearer YOUR_JWT_TOKEN' \
--header 'Accept: application/json, text/plain, */*'
```

**Expected Response:**
```json
{
  "success": true,
  "connected": false,
  "message": "No Google OAuth connection found. OAuth flow initiated.",
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "state": "Fvy_Ooa6Q290wgA2eR8F7stzDUz2cGOr4YVY9FyE450",
  "requires_reauth": false
}
```

### **Test 2: User with Valid Google OAuth**
```bash
curl --location 'http://localhost:8000/accounts/api/google-oauth/connect/' \
--header 'Authorization: Bearer YOUR_JWT_TOKEN' \
--header 'Accept: application/json, text/plain, */*'
```

**Expected Response:**
```json
{
  "success": true,
  "connected": true,
  "message": "Google OAuth connection is active and valid",
  "google_auth": {
    "id": 2,
    "google_email": "kstarbootcamp@gmail.com",
    "google_name": "KSTAR TECH",
    "scopes": "https://www.googleapis.com/auth/adwords...",
    "is_active": true,
    "last_used": "2025-09-03T09:07:10.627248+00:00Z",
    "token_expiry": "2025-09-03T10:07:09.379295+00:00Z",
    "is_token_expired": false,
    "needs_refresh": false
  }
}
```

### **Test 3: Production URL**
```bash
curl --location 'https://your-api-domain.com/accounts/api/google-oauth/connect/' \
--header 'Authorization: Bearer YOUR_JWT_TOKEN' \
--header 'Accept: application/json, text/plain, */*'
```

## 🔄 **API Logic Flow**

### **Step 1: Check Existing Connection**
```python
auth_service = UserGoogleAuthService()
auth_record = auth_service.get_valid_auth(request.user)
```

### **Step 2: Handle Different Scenarios**

#### **Scenario A: Valid Connection**
```python
if auth_record and not auth_record.is_token_expired():
    # Return connection details
    return {
        'success': True,
        'connected': True,
        'message': 'Google OAuth connection is active and valid',
        'google_auth': { ... }
    }
```

#### **Scenario B: Expired Token**
```python
if auth_record and auth_record.is_token_expired():
    # Try to refresh token
    refreshed_record = auth_service.refresh_user_tokens(request.user)
    if refreshed_record:
        # Return refreshed connection details
    else:
        # Return 401 - requires reauth
```

#### **Scenario C: No Connection**
```python
if not auth_record:
    # Generate OAuth URL and initiate flow
    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state
    
    google_oauth_url = build_google_oauth_url(state)
    
    return {
        'success': True,
        'connected': False,
        'message': 'No Google OAuth connection found. OAuth flow initiated.',
        'authorization_url': google_oauth_url,
        'state': state,
        'requires_reauth': False
    }
```

## 🎯 **New Features**

### **1. Automatic OAuth Flow Initiation**
- **When**: No Google OAuth connection exists
- **What**: Generates Google OAuth authorization URL
- **Response**: Includes `authorization_url` and `state` for frontend to redirect user

### **2. State Parameter for Security**
- **Purpose**: CSRF protection during OAuth flow
- **Generation**: Random 32-character URL-safe string
- **Storage**: Stored in user session for validation

### **3. Complete OAuth URL Generation**
- **Client ID**: From Django settings
- **Redirect URI**: From Django settings
- **Scopes**: Google Ads, Analytics, User Info permissions
- **Parameters**: `access_type=offline`, `prompt=consent`

## 🔗 **Frontend Integration**

### **1. Check Connection Status**
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
    
    if (data.success) {
      if (data.connected) {
        // User has valid Google OAuth connection
        console.log('Google OAuth connected:', data.google_auth);
        return { connected: true, auth: data.google_auth };
      } else {
        // User needs to complete OAuth flow
        console.log('OAuth flow initiated:', data.authorization_url);
        return { 
          connected: false, 
          authorizationUrl: data.authorization_url,
          state: data.state 
        };
      }
    }
  } catch (error) {
    console.error('Error checking Google connection:', error);
    return { connected: false, error: error.message };
  }
}
```

### **2. Handle OAuth Flow**
```javascript
async function initiateGoogleOAuth() {
  const connectionStatus = await checkGoogleConnection();
  
  if (!connectionStatus.connected && connectionStatus.authorizationUrl) {
    // Redirect user to Google OAuth
    window.location.href = connectionStatus.authorizationUrl;
  } else if (connectionStatus.connected) {
    // User already connected, proceed with Google Ads features
    console.log('Ready to use Google Ads features');
  }
}
```

### **3. React Component Integration**
```jsx
import { useState, useEffect } from 'react';

function GoogleConnectionManager() {
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
  
  const handleConnectGoogle = () => {
    if (connectionStatus?.authorization_url) {
      window.location.href = connectionStatus.authorization_url;
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
          <h3>🔗 Connect Google Account</h3>
          <p>{connectionStatus?.message || 'Connect your Google account to access Google Ads features'}</p>
          <button onClick={handleConnectGoogle}>
            Connect Google Account
          </button>
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

### **2. State Parameter**
- Random 32-character string for CSRF protection
- Stored in user session for validation
- Included in OAuth URL for Google to return

### **3. Token Validation**
- Checks token expiry automatically
- Refreshes tokens when possible
- Handles refresh failures gracefully

### **4. Error Handling**
- Secure error messages
- Proper HTTP status codes
- CORS headers included

## 📊 **Response Field Descriptions**

### **Success Response Fields:**
- **`success`**: Boolean indicating API call success
- **`connected`**: Boolean indicating OAuth connection status
- **`message`**: Human-readable status message
- **`google_auth`**: OAuth connection details (when connected)
  - **`id`**: Database ID of the connection
  - **`google_email`**: User's Google account email
  - **`google_name`**: User's Google account display name
  - **`scopes`**: Granted OAuth permissions
  - **`is_active`**: Connection status
  - **`last_used`**: Last usage timestamp (ISO format)
  - **`token_expiry`**: Token expiration time (ISO format)
  - **`is_token_expired`**: Boolean indicating if token is expired
  - **`needs_refresh`**: Boolean indicating if token needs refresh
- **`authorization_url`**: Google OAuth URL (when initiating flow)
- **`state`**: CSRF protection state parameter (when initiating flow)
- **`requires_reauth`**: Boolean indicating if reauthentication is needed

### **Error Response Fields:**
- **`success`**: Boolean indicating API call failure
- **`connected`**: Boolean indicating no connection
- **`error`**: Error message describing the issue
- **`requires_reauth`**: Boolean indicating reauthentication needed

## 🔗 **Integration with Other APIs**

### **1. Use with ad_expert API**
```javascript
async function useAdExpertAPI() {
  // Check Google OAuth connection first
  const connectionStatus = await checkGoogleConnection();
  
  if (connectionStatus.connected) {
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
    // Initiate OAuth flow
    window.location.href = connectionStatus.authorizationUrl;
  }
}
```

### **2. Use with Google Ads Accounts API**
```javascript
async function getGoogleAdsAccounts() {
  const connectionStatus = await checkGoogleConnection();
  
  if (connectionStatus.connected) {
    const response = await fetch('/accounts/api/google-oauth/ads-accounts/', {
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Accept': 'application/json'
      }
    });
    
    return await response.json();
  } else {
    throw new Error('Google OAuth connection required');
  }
}
```

## ⚠️ **Important Notes**

1. **JWT Token Required**: API requires valid JWT authentication
2. **Automatic OAuth Initiation**: No connection triggers OAuth flow automatically
3. **State Parameter**: CSRF protection during OAuth flow
4. **Token Refresh**: Automatic refresh when tokens are expired
5. **CORS Enabled**: Headers set for cross-origin requests
6. **Error Handling**: Comprehensive error handling with proper status codes

## 🎯 **Summary**

The updated `/api/google-oauth/connect/` API now provides:

- ✅ **Complete OAuth flow management** in a single call
- ✅ **Automatic OAuth initiation** for first-time users
- ✅ **Token validation and refresh** for existing connections
- ✅ **Clear connection status** with detailed information
- ✅ **Proper error handling** with HTTP status codes
- ✅ **Frontend-friendly responses** with boolean flags
- ✅ **Security features** with JWT authentication and CSRF protection
- ✅ **CORS support** for cross-origin requests

**Perfect for frontend applications that need complete Google OAuth management in one API call!** 🚀

