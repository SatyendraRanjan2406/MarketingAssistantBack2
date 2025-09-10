# Google Ads & Meta Ads OAuth Connection - Curl Examples

## 🔗 **Google Ads OAuth Connection**

### **1. Initiate Google OAuth Flow**
```bash
curl -X GET http://localhost:8000/accounts/api/google-oauth/initiate/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response (200):**
```json
{
  "success": true,
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&response_type=code&scope=https://www.googleapis.com/auth/adwords&state=...",
  "state": "google_state_token",
  "local_state": "user_1_1640995200"
}
```

### **2. Handle OAuth Callback (Browser Redirect)**
```bash
# This is typically handled by browser redirect, but for testing:
curl -X GET "http://localhost:8000/accounts/api/google-oauth/callback/?code=AUTH_CODE_FROM_GOOGLE&state=STATE_TOKEN"
```

### **3. Exchange OAuth Code for Tokens (Frontend Integration)**
```bash
curl -X POST http://localhost:8000/accounts/api/google-oauth/exchange-tokens/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "AUTH_CODE_FROM_GOOGLE",
    "state": "user_1_1640995200"
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Google OAuth successful!",
  "google_auth": {
    "id": 1,
    "google_email": "user@gmail.com",
    "google_name": "John Doe",
    "scopes": "https://www.googleapis.com/auth/adwords",
    "is_active": true
  }
}
```

### **4. Check Google OAuth Status**
```bash
curl -X GET http://localhost:8000/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response (200):**
```json
{
  "success": true,
  "connected": true,
  "google_auth": {
    "id": 1,
    "google_email": "user@gmail.com",
    "google_name": "John Doe",
    "scopes": "https://www.googleapis.com/auth/adwords",
    "is_active": true,
    "last_used": "2025-01-27T12:00:00Z",
    "token_expiry": "2025-01-27T13:00:00Z"
  }
}
```

### **5. Get Google Ads Accounts**
```bash
curl -X GET http://localhost:8000/accounts/api/google-oauth/ads-accounts/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response (200):**
```json
{
  "success": true,
  "accounts": [
    {
      "customer_id": "9762343117",
      "descriptive_name": "John's Ads Account",
      "currency_code": "USD",
      "time_zone": "America/New_York",
      "manager": false
    }
  ],
  "count": 1
}
```

### **6. Disconnect Google OAuth**
```bash
curl -X POST http://localhost:8000/accounts/api/google-oauth/disconnect/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Google OAuth disconnected successfully!"
}
```

## 📱 **Meta Ads OAuth Connection**

### **1. Initiate Meta OAuth Flow**
```bash
curl -X GET http://localhost:8000/accounts/api/meta-oauth/initiate/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response (200):**
```json
{
  "success": true,
  "authorization_url": "https://www.facebook.com/v20.0/dialog/oauth?client_id=...&redirect_uri=...&response_type=code&scope=ads_read,ads_management&state=...",
  "state": "meta_state_token",
  "local_state": "user_1_1640995200"
}
```

### **2. Handle Meta OAuth Callback**
```bash
curl -X GET "http://localhost:8000/accounts/api/meta-oauth/callback/?code=AUTH_CODE_FROM_META&state=STATE_TOKEN"
```

### **3. Exchange Meta OAuth Code for Tokens**
```bash
curl -X POST http://localhost:8000/accounts/api/meta-oauth/exchange-tokens/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "AUTH_CODE_FROM_META",
    "state": "user_1_1640995200"
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Meta OAuth successful!",
  "meta_auth": {
    "id": 1,
    "meta_email": "user@facebook.com",
    "meta_name": "John Doe",
    "scopes": "ads_read,ads_management",
    "is_active": true
  }
}
```

### **4. Check Meta OAuth Status**
```bash
curl -X GET http://localhost:8000/accounts/api/meta-oauth/status/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response (200):**
```json
{
  "success": true,
  "connected": true,
  "meta_auth": {
    "id": 1,
    "meta_email": "user@facebook.com",
    "meta_name": "John Doe",
    "scopes": "ads_read,ads_management",
    "is_active": true,
    "last_used": "2025-01-27T12:00:00Z",
    "token_expiry": "2025-01-27T13:00:00Z"
  }
}
```

### **5. Get Meta Ad Accounts**
```bash
curl -X GET http://localhost:8000/accounts/api/meta-oauth/ad-accounts/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response (200):**
```json
{
  "success": true,
  "accounts": [
    {
      "account_id": "act_123456789",
      "account_name": "John's Ad Account",
      "currency": "USD",
      "timezone": "America/New_York",
      "account_status": "ACTIVE"
    }
  ],
  "count": 1
}
```

### **6. Disconnect Meta OAuth**
```bash
curl -X POST http://localhost:8000/accounts/api/meta-oauth/disconnect/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Meta OAuth disconnected successfully!"
}
```

## 🔄 **Complete OAuth Flow Examples**

### **Google Ads Complete Flow**
```bash
# 1. Get JWT token from signin
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }')

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.data.tokens.access_token')

# 2. Initiate Google OAuth
OAUTH_RESPONSE=$(curl -s -X GET http://localhost:8000/accounts/api/google-oauth/initiate/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")

AUTH_URL=$(echo $OAUTH_RESPONSE | jq -r '.authorization_url')
STATE=$(echo $OAUTH_RESPONSE | jq -r '.state')

echo "Visit this URL to authorize: $AUTH_URL"

# 3. After user authorizes, exchange code for tokens
curl -X POST http://localhost:8000/accounts/api/google-oauth/exchange-tokens/ \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": \"AUTH_CODE_FROM_GOOGLE\",
    \"state\": \"$STATE\"
  }"

# 4. Check connection status
curl -X GET http://localhost:8000/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 5. Get Google Ads accounts
curl -X GET http://localhost:8000/accounts/api/google-oauth/ads-accounts/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### **Meta Ads Complete Flow**
```bash
# 1. Get JWT token from signin
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }')

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.data.tokens.access_token')

# 2. Initiate Meta OAuth
OAUTH_RESPONSE=$(curl -s -X GET http://localhost:8000/accounts/api/meta-oauth/initiate/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")

AUTH_URL=$(echo $OAUTH_RESPONSE | jq -r '.authorization_url')
STATE=$(echo $OAUTH_RESPONSE | jq -r '.state')

echo "Visit this URL to authorize: $AUTH_URL"

# 3. After user authorizes, exchange code for tokens
curl -X POST http://localhost:8000/accounts/api/meta-oauth/exchange-tokens/ \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": \"AUTH_CODE_FROM_META\",
    \"state\": \"$STATE\"
  }"

# 4. Check connection status
curl -X GET http://localhost:8000/accounts/api/meta-oauth/status/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 5. Get Meta ad accounts
curl -X GET http://localhost:8000/accounts/api/meta-oauth/ad-accounts/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 🧪 **Testing OAuth Connections**

### **Test Google Ads Connection**
```bash
# 1. Signin to get JWT token
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# 2. Initiate Google OAuth (use the access_token from step 1)
curl -X GET http://localhost:8000/accounts/api/google-oauth/initiate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. Check if already connected
curl -X GET http://localhost:8000/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **Test Meta Ads Connection**
```bash
# 1. Signin to get JWT token
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# 2. Initiate Meta OAuth (use the access_token from step 1)
curl -X GET http://localhost:8000/accounts/api/meta-oauth/initiate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. Check if already connected
curl -X GET http://localhost:8000/accounts/api/meta-oauth/status/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔗 **Integration with ad_expert API**

Once OAuth connections are established, you can use them with the ad_expert API:

```bash
# Use JWT token with ad_expert API
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for Google Ads customer ID 9762343117?"
  }'
```

## 📝 **OAuth Scopes**

### **Google Ads Scopes**
- `https://www.googleapis.com/auth/adwords` - Full access to Google Ads API

### **Meta Ads Scopes**
- `ads_read` - Read access to ad accounts
- `ads_management` - Manage ad accounts and campaigns

## 🚀 **Production URLs**

Replace `http://localhost:8000` with your production domain:

```bash
# Production Google OAuth
curl -X GET https://your-api-domain.com/accounts/api/google-oauth/initiate/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Production Meta OAuth
curl -X GET https://your-api-domain.com/accounts/api/meta-oauth/initiate/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## ⚠️ **Important Notes**

1. **JWT Token Required**: All OAuth endpoints require a valid JWT token
2. **State Parameter**: Used for CSRF protection in OAuth flows
3. **Authorization URLs**: Must be opened in browser for user consent
4. **Token Expiry**: OAuth tokens are automatically refreshed when needed
5. **Error Handling**: All endpoints return consistent error formats
6. **CORS**: Headers are set for cross-origin requests

The OAuth connections are now ready for integration with Google Ads and Meta Ads APIs!

