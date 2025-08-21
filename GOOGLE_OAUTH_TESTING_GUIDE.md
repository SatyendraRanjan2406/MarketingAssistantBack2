# Google OAuth Testing Guide with cURL Commands

This guide provides step-by-step testing instructions and cURL commands for the Google OAuth integration.

## 🚀 **Quick Start Testing**

### **1. Set Up Environment Variables**
Create a `.env` file in your project root with these variables:

```bash
# Copy from env_template_complete.txt
cp env_template_complete.txt .env

# Edit .env file with your actual values
nano .env
```

**Required Google OAuth Variables:**
```bash
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret_here
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8001/accounts/api/google-oauth/callback/
```

### **2. Start Django Server**
```bash
python manage.py runserver 8001
```

### **3. Test Server Health**
```bash
curl http://localhost:8001/accounts/api/test-cors/
```

## 🔑 **Step 0: Get Google OAuth Credentials**

### **0.1 Google Cloud Console Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Google+ API
   - Google Ads API
   - Google Analytics API (optional)

### **0.2 Create OAuth 2.0 Credentials**
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. Choose **Web application**
4. Add authorized redirect URIs:
   - `http://localhost:8001/accounts/api/google-oauth/callback/` (development)
   - `https://yourdomain.com/accounts/api/google-oauth/callback/` (production)
5. Copy **Client ID** and **Client Secret**

### **0.3 Update Your .env File**
```bash
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your_secret_here
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8001/accounts/api/google-oauth/callback/
```

---

## 🔐 **Step 1: User Authentication (JWT)**

### **1.1 Create User Account**
```bash
curl -X POST http://localhost:8001/accounts/api/signup/ \
  -H "Content-Type: application/json" \
  -H "Access-Control-Allow-Credentials: true" \
  -d '{
    "username": "testuser_oauth",
    "email": "testuser_oauth@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "company_name": "Test Company",
    "phone_number": "+1234567890",
    "address": "123 Test Street, Test City"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "User created successfully!",
  "user": {
    "id": 1,
    "username": "testuser_oauth",
    "email": "testuser_oauth@example.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "profile": {
    "company_name": "Test Company",
    "phone_number": "+1234567890",
    "address": "123 Test Street, Test City"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **1.2 Login User**
```bash
curl -X POST http://localhost:8001/accounts/api/signin/ \
  -H "Content-Type: application/json" \
  -H "Access-Control-Allow-Credentials: true" \
  -d '{
    "username": "testuser_oauth",
    "password": "testpass123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful!",
  "user": {
    "id": 1,
    "username": "testuser_oauth",
    "email": "testuser_oauth@example.com"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJIUzI1NiJ9..."
}
```

**Save the `access_token` for subsequent requests!**

## 🔗 **Step 2: Google OAuth Flow**

### **2.1 Initiate OAuth (Get Authorization URL)**
```bash
# Replace YOUR_ACCESS_TOKEN with the token from login
curl -X GET http://localhost:8001/accounts/api/google-oauth/initiate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": true,
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?client_id=...&redirect_uri=...&scope=...&response_type=code&access_type=offline&include_granted_scopes=true&prompt=consent&state=user_1_1234567890",
  "state": "user_1_1234567890"
}
```

### **2.2 Manual OAuth Flow (Browser Required)**

1. **Copy the `authorization_url`** from the previous response
2. **Open in browser** - this will redirect to Google's OAuth consent screen
3. **Sign in with Google** account that has Google Ads access
4. **Grant permissions** for the requested scopes
5. **Google will redirect** to your callback URL with an authorization code

**Example redirect URL:**
```
http://localhost:8001/accounts/api/google-oauth/callback/?code=4/0AfJohXn...&state=user_1_1234567890
```

### **2.3 Exchange Code for Tokens (Callback)**
```bash
# Use the code and state from the browser redirect
curl -X GET "http://localhost:8001/accounts/api/google-oauth/callback/?code=4/0AfJohXn...&state=user_1_1234567890" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Google OAuth successful!",
  "google_auth": {
    "id": 1,
    "google_email": "your.email@gmail.com",
    "google_name": "Your Name",
    "scopes": "https://www.googleapis.com/auth/userinfo.profile,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/analytics.readonly",
    "is_active": true
  }
}
```

## 📊 **Step 3: OAuth Status & Management**

### **3.1 Check OAuth Connection Status**
```bash
curl -X GET http://localhost:8001/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response (Connected):**
```json
{
  "success": true,
  "connected": true,
  "google_auth": {
    "id": 1,
    "google_email": "your.email@gmail.com",
    "google_name": "Your Name",
    "scopes": "https://www.googleapis.com/auth/userinfo.profile,...",
    "is_active": true,
    "last_used": "2025-08-18T10:30:00Z",
    "token_expiry": "2025-08-18T11:30:00Z"
  }
}
```

**Expected Response (Not Connected):**
```json
{
  "success": true,
  "connected": false,
  "message": "No active Google OAuth connection"
}
```

### **3.2 Get Google Ads Accounts**
```bash
curl -X GET http://localhost:8001/accounts/api/google-oauth/ads-accounts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": true,
  "accounts": [
    {
      "customer_id": "1234567890",
      "name": "My Google Ads Account",
      "currency_code": "USD",
      "time_zone": "America/New_York",
      "can_manage_clients": true
    }
  ],
  "count": 1
}
```

### **3.3 Disconnect OAuth Connection**
```bash
curl -X POST http://localhost:8001/accounts/api/google-oauth/disconnect/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Google OAuth disconnected successfully"
}
```

## 🔄 **Step 4: Token Management**

### **4.1 Refresh Access Token**
```bash
# This happens automatically when calling protected endpoints
# But you can test by calling any OAuth endpoint with an expired token
curl -X GET http://localhost:8001/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer EXPIRED_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

### **4.2 Test Token Validation**
```bash
# Check if your current token is still valid
curl -X GET http://localhost:8001/accounts/api/dashboard/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

## 🧪 **Step 5: Error Testing**

### **5.1 Test with Invalid Token**
```bash
curl -X GET http://localhost:8001/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer INVALID_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "detail": "Given token not valid for any token type"
}
```

### **5.2 Test OAuth Initiate Without Auth**
```bash
curl -X GET http://localhost:8001/accounts/api/google-oauth/initiate/ \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### **5.3 Test Invalid OAuth Callback**
```bash
curl -X GET "http://localhost:8001/accounts/api/google-oauth/callback/?error=access_denied&state=invalid_state" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": false,
  "error": "OAuth error: access_denied"
}
```

## 📝 **Complete Testing Script**

### **Bash Script for Automated Testing**
```bash
#!/bin/bash

# Google OAuth Testing Script
BASE_URL="http://localhost:8001"
ACCESS_TOKEN=""

echo "🚀 Starting Google OAuth Testing..."

# Step 1: Create user
echo "📝 Creating test user..."
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/accounts/api/signup/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser_oauth_$(date +%s)",
    "email": "testuser_oauth_$(date +%s)@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "company_name": "Test Company"
  }')

echo "Create Response: $CREATE_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo $CREATE_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to get access token"
    exit 1
fi

echo "✅ Access Token: $ACCESS_TOKEN"

# Step 2: Check OAuth status (should be disconnected)
echo "🔍 Checking OAuth status..."
curl -s -X GET "$BASE_URL/accounts/api/google-oauth/status/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"

# Step 3: Initiate OAuth
echo "🔗 Initiating OAuth..."
OAUTH_RESPONSE=$(curl -s -X GET "$BASE_URL/accounts/api/google-oauth/initiate/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true")

echo "OAuth Response: $OAUTH_RESPONSE"

# Extract authorization URL
AUTH_URL=$(echo $OAUTH_RESPONSE | grep -o '"authorization_url":"[^"]*"' | cut -d'"' -f4)

if [ -n "$AUTH_URL" ]; then
    echo "✅ Authorization URL: $AUTH_URL"
    echo "🌐 Please open this URL in your browser to complete OAuth"
    echo "📋 After OAuth, copy the callback URL and run the callback test"
else
    echo "❌ Failed to get authorization URL"
fi

echo "🎯 Testing complete! Check the responses above."
```

## 🔍 **Troubleshooting**

### **Common Issues & Solutions**

1. **"Port already in use"**
   ```bash
   # Kill existing Django processes
   pkill -f "python manage.py runserver"
   # Or use different port
   python manage.py runserver 8001
   ```

2. **"Module not found" errors**
   ```bash
   # Install missing packages
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

3. **"CSRF verification failed"**
   - All OAuth endpoints are CSRF-exempt
   - Ensure you're using the correct headers

4. **"Authentication credentials not provided"**
   - Include `Authorization: Bearer YOUR_TOKEN` header
   - Ensure token is valid and not expired

5. **OAuth callback errors**
   - Check redirect URI in Google Cloud Console
   - Verify state parameter matches
   - Ensure authorization code is valid

## 📊 **Expected Database State**

After successful OAuth:

```sql
-- Check UserGoogleAuth table
SELECT 
    u.username,
    uga.google_email,
    uga.google_name,
    uga.is_active,
    uga.created_at
FROM accounts_usergoogleauth uga
JOIN auth_user u ON uga.user_id = u.id;

-- Check token expiry
SELECT 
    google_email,
    token_expiry,
    is_active,
    error_count
FROM accounts_usergoogleauth
WHERE is_active = true;
```

## 🎯 **Next Steps After Testing**

1. **Verify OAuth flow** works end-to-end
2. **Test token refresh** functionality
3. **Validate Google Ads** account access
4. **Implement frontend** integration
5. **Add error handling** for production use

---

**Happy Testing! 🚀** Use these cURL commands to verify your Google OAuth integration is working correctly.

This guide provides step-by-step testing instructions and cURL commands for the Google OAuth integration.

## 🚀 **Quick Start Testing**

### **1. Set Up Environment Variables**
Create a `.env` file in your project root with these variables:

```bash
# Copy from env_template_complete.txt
cp env_template_complete.txt .env

# Edit .env file with your actual values
nano .env
```

**Required Google OAuth Variables:**
```bash
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret_here
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8001/accounts/api/google-oauth/callback/
```

### **2. Start Django Server**
```bash
python manage.py runserver 8001
```

### **3. Test Server Health**
```bash
curl http://localhost:8001/accounts/api/test-cors/
```

## 🔑 **Step 0: Get Google OAuth Credentials**

### **0.1 Google Cloud Console Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Google+ API
   - Google Ads API
   - Google Analytics API (optional)

### **0.2 Create OAuth 2.0 Credentials**
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. Choose **Web application**
4. Add authorized redirect URIs:
   - `http://localhost:8001/accounts/api/google-oauth/callback/` (development)
   - `https://yourdomain.com/accounts/api/google-oauth/callback/` (production)
5. Copy **Client ID** and **Client Secret**

### **0.3 Update Your .env File**
```bash
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your_secret_here
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8001/accounts/api/google-oauth/callback/
```

---

## 🔐 **Step 1: User Authentication (JWT)**

### **1.1 Create User Account**
```bash
curl -X POST http://localhost:8001/accounts/api/signup/ \
  -H "Content-Type: application/json" \
  -H "Access-Control-Allow-Credentials: true" \
  -d '{
    "username": "testuser_oauth",
    "email": "testuser_oauth@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "company_name": "Test Company",
    "phone_number": "+1234567890",
    "address": "123 Test Street, Test City"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "User created successfully!",
  "user": {
    "id": 1,
    "username": "testuser_oauth",
    "email": "testuser_oauth@example.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "profile": {
    "company_name": "Test Company",
    "phone_number": "+1234567890",
    "address": "123 Test Street, Test City"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **1.2 Login User**
```bash
curl -X POST http://localhost:8001/accounts/api/signin/ \
  -H "Content-Type: application/json" \
  -H "Access-Control-Allow-Credentials: true" \
  -d '{
    "username": "testuser_oauth",
    "password": "testpass123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful!",
  "user": {
    "id": 1,
    "username": "testuser_oauth",
    "email": "testuser_oauth@example.com"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJIUzI1NiJ9..."
}
```

**Save the `access_token` for subsequent requests!**

## 🔗 **Step 2: Google OAuth Flow**

### **2.1 Initiate OAuth (Get Authorization URL)**
```bash
# Replace YOUR_ACCESS_TOKEN with the token from login
curl -X GET http://localhost:8001/accounts/api/google-oauth/initiate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": true,
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?client_id=...&redirect_uri=...&scope=...&response_type=code&access_type=offline&include_granted_scopes=true&prompt=consent&state=user_1_1234567890",
  "state": "user_1_1234567890"
}
```

### **2.2 Manual OAuth Flow (Browser Required)**

1. **Copy the `authorization_url`** from the previous response
2. **Open in browser** - this will redirect to Google's OAuth consent screen
3. **Sign in with Google** account that has Google Ads access
4. **Grant permissions** for the requested scopes
5. **Google will redirect** to your callback URL with an authorization code

**Example redirect URL:**
```
http://localhost:8001/accounts/api/google-oauth/callback/?code=4/0AfJohXn...&state=user_1_1234567890
```

### **2.3 Exchange Code for Tokens (Callback)**
```bash
# Use the code and state from the browser redirect
curl -X GET "http://localhost:8001/accounts/api/google-oauth/callback/?code=4/0AfJohXn...&state=user_1_1234567890" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Google OAuth successful!",
  "google_auth": {
    "id": 1,
    "google_email": "your.email@gmail.com",
    "google_name": "Your Name",
    "scopes": "https://www.googleapis.com/auth/userinfo.profile,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/analytics.readonly",
    "is_active": true
  }
}
```

## 📊 **Step 3: OAuth Status & Management**

### **3.1 Check OAuth Connection Status**
```bash
curl -X GET http://localhost:8001/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response (Connected):**
```json
{
  "success": true,
  "connected": true,
  "google_auth": {
    "id": 1,
    "google_email": "your.email@gmail.com",
    "google_name": "Your Name",
    "scopes": "https://www.googleapis.com/auth/userinfo.profile,...",
    "is_active": true,
    "last_used": "2025-08-18T10:30:00Z",
    "token_expiry": "2025-08-18T11:30:00Z"
  }
}
```

**Expected Response (Not Connected):**
```json
{
  "success": true,
  "connected": false,
  "message": "No active Google OAuth connection"
}
```

### **3.2 Get Google Ads Accounts**
```bash
curl -X GET http://localhost:8001/accounts/api/google-oauth/ads-accounts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": true,
  "accounts": [
    {
      "customer_id": "1234567890",
      "name": "My Google Ads Account",
      "currency_code": "USD",
      "time_zone": "America/New_York",
      "can_manage_clients": true
    }
  ],
  "count": 1
}
```

### **3.3 Disconnect OAuth Connection**
```bash
curl -X POST http://localhost:8001/accounts/api/google-oauth/disconnect/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Google OAuth disconnected successfully"
}
```

## 🔄 **Step 4: Token Management**

### **4.1 Refresh Access Token**
```bash
# This happens automatically when calling protected endpoints
# But you can test by calling any OAuth endpoint with an expired token
curl -X GET http://localhost:8001/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer EXPIRED_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

### **4.2 Test Token Validation**
```bash
# Check if your current token is still valid
curl -X GET http://localhost:8001/accounts/api/dashboard/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

## 🧪 **Step 5: Error Testing**

### **5.1 Test with Invalid Token**
```bash
curl -X GET http://localhost:8001/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer INVALID_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "detail": "Given token not valid for any token type"
}
```

### **5.2 Test OAuth Initiate Without Auth**
```bash
curl -X GET http://localhost:8001/accounts/api/google-oauth/initiate/ \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### **5.3 Test Invalid OAuth Callback**
```bash
curl -X GET "http://localhost:8001/accounts/api/google-oauth/callback/?error=access_denied&state=invalid_state" \
  -H "Access-Control-Allow-Credentials: true"
```

**Expected Response:**
```json
{
  "success": false,
  "error": "OAuth error: access_denied"
}
```

## 📝 **Complete Testing Script**

### **Bash Script for Automated Testing**
```bash
#!/bin/bash

# Google OAuth Testing Script
BASE_URL="http://localhost:8001"
ACCESS_TOKEN=""

echo "🚀 Starting Google OAuth Testing..."

# Step 1: Create user
echo "📝 Creating test user..."
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/accounts/api/signup/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser_oauth_$(date +%s)",
    "email": "testuser_oauth_$(date +%s)@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "company_name": "Test Company"
  }')

echo "Create Response: $CREATE_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo $CREATE_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to get access token"
    exit 1
fi

echo "✅ Access Token: $ACCESS_TOKEN"

# Step 2: Check OAuth status (should be disconnected)
echo "🔍 Checking OAuth status..."
curl -s -X GET "$BASE_URL/accounts/api/google-oauth/status/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true"

# Step 3: Initiate OAuth
echo "🔗 Initiating OAuth..."
OAUTH_RESPONSE=$(curl -s -X GET "$BASE_URL/accounts/api/google-oauth/initiate/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Access-Control-Allow-Credentials: true")

echo "OAuth Response: $OAUTH_RESPONSE"

# Extract authorization URL
AUTH_URL=$(echo $OAUTH_RESPONSE | grep -o '"authorization_url":"[^"]*"' | cut -d'"' -f4)

if [ -n "$AUTH_URL" ]; then
    echo "✅ Authorization URL: $AUTH_URL"
    echo "🌐 Please open this URL in your browser to complete OAuth"
    echo "📋 After OAuth, copy the callback URL and run the callback test"
else
    echo "❌ Failed to get authorization URL"
fi

echo "🎯 Testing complete! Check the responses above."
```

## 🔍 **Troubleshooting**

### **Common Issues & Solutions**

1. **"Port already in use"**
   ```bash
   # Kill existing Django processes
   pkill -f "python manage.py runserver"
   # Or use different port
   python manage.py runserver 8001
   ```

2. **"Module not found" errors**
   ```bash
   # Install missing packages
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

3. **"CSRF verification failed"**
   - All OAuth endpoints are CSRF-exempt
   - Ensure you're using the correct headers

4. **"Authentication credentials not provided"**
   - Include `Authorization: Bearer YOUR_TOKEN` header
   - Ensure token is valid and not expired

5. **OAuth callback errors**
   - Check redirect URI in Google Cloud Console
   - Verify state parameter matches
   - Ensure authorization code is valid

## 📊 **Expected Database State**

After successful OAuth:

```sql
-- Check UserGoogleAuth table
SELECT 
    u.username,
    uga.google_email,
    uga.google_name,
    uga.is_active,
    uga.created_at
FROM accounts_usergoogleauth uga
JOIN auth_user u ON uga.user_id = u.id;

-- Check token expiry
SELECT 
    google_email,
    token_expiry,
    is_active,
    error_count
FROM accounts_usergoogleauth
WHERE is_active = true;
```

## 🎯 **Next Steps After Testing**

1. **Verify OAuth flow** works end-to-end
2. **Test token refresh** functionality
3. **Validate Google Ads** account access
4. **Implement frontend** integration
5. **Add error handling** for production use

---

**Happy Testing! 🚀** Use these cURL commands to verify your Google OAuth integration is working correctly.
