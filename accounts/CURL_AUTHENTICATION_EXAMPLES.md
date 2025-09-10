# Authentication API - Curl Examples

## 🔐 **Email/Password Authentication**

### **1. User Registration (Signup)**
```bash
curl -X POST http://localhost:8000/accounts/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "name": "John Doe"
  }'
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Account created successfully",
  "data": {
    "user": {
      "id": "3",
      "email": "john@example.com",
      "name": "John Doe",
      "provider": "email",
      "created_at": "2025-01-27T12:00:00Z",
      "updated_at": "2025-01-27T12:00:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    }
  }
}
```

**Error Response - Email Used for Google Auth (400):**
```json
{
  "success": false,
  "error": "Email used for google auth. use another email"
}
```

### **2. User Login (Signin)**
```bash
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "6",
      "email": "john@example.com",
      "name": "John Doe",
      "provider": "email",
      "created_at": "2025-09-03T08:08:40.412696+00:00Z",
      "updated_at": "2025-09-03T08:08:40.412696+00:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    }
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Invalid email or password."
}
```

### **4. Token Refresh**
```bash
curl -X POST http://localhost:8000/accounts/api/refresh-token/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Token refreshed successfully!",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### **5. Secure Logout**
```bash
curl -X POST http://localhost:8000/accounts/api/logout/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully!"
}
```

## 🔗 **Google OAuth Authentication**

### **6. Initiate Google OAuth Flow**
```bash
curl -X GET http://localhost:8000/accounts/api/google-oauth/initiate/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200):**
```json
{
  "success": true,
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "state": "google_state_token",
  "local_state": "user_1_1640995200"
}
```

### **7. Google OAuth Callback (Browser Redirect)**
```bash
# This is typically handled by browser redirect, but for testing:
curl -X GET "http://localhost:8000/accounts/api/google-oauth/callback/?code=AUTH_CODE&state=STATE_TOKEN"
```

### **8. Exchange OAuth Code for Tokens**
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
    "google_email": "john@gmail.com",
    "google_name": "John Doe",
    "scopes": "https://www.googleapis.com/auth/adwords",
    "is_active": true
  }
}
```

### **9. Check Google OAuth Status**
```bash
curl -X GET http://localhost:8000/accounts/api/google-oauth/status/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200):**
```json
{
  "success": true,
  "connected": true,
  "google_auth": {
    "id": 1,
    "google_email": "john@gmail.com",
    "google_name": "John Doe",
    "scopes": "https://www.googleapis.com/auth/adwords",
    "is_active": true,
    "last_used": "2025-01-27T12:00:00Z",
    "token_expiry": "2025-01-27T13:00:00Z"
  }
}
```

### **10. Disconnect Google OAuth**
```bash
curl -X POST http://localhost:8000/accounts/api/google-oauth/disconnect/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Google OAuth disconnected successfully!"
}
```

### **11. Get Google Ads Accounts**
```bash
curl -X GET http://localhost:8000/accounts/api/google-oauth/ads-accounts/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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

## 👤 **User Management**

### **12. Get User Dashboard**
```bash
curl -X GET http://localhost:8000/accounts/api/dashboard/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Welcome to your dashboard!",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Acme Corp",
    "phone_number": "+1-555-123-4567",
    "address": "123 Main St, City, State"
  }
}
```

### **13. Update User Profile**
```bash
curl -X POST http://localhost:8000/accounts/api/profile/update/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@example.com",
    "company_name": "New Company Inc",
    "phone_number": "+1-555-987-6543",
    "address": "456 Oak Ave, New City, State"
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully!"
}
```

### **14. Get Google Account Status**
```bash
curl -X GET http://localhost:8000/accounts/api/google-account/status/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200):**
```json
{
  "success": true,
  "google_account": {
    "is_connected": true,
    "accounts": [
      {
        "id": 1,
        "google_email": "john@gmail.com",
        "google_name": "John Doe",
        "google_ads_customer_id": "9762343117",
        "google_ads_account_name": "John's Ads Account",
        "is_connected": true,
        "last_used": "2025-01-27T12:00:00Z",
        "scopes": ["https://www.googleapis.com/auth/adwords"],
        "token_expiry": "2025-01-27T13:00:00Z",
        "is_token_expired": false,
        "needs_refresh": false
      }
    ],
    "total_accounts": 1
  }
}
```

## 🧪 **Testing Scenarios**

### **Test 1: Complete Signup Flow**
```bash
# 1. Signup
curl -X POST http://localhost:8000/accounts/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User"
  }'

# 2. Signin with email
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### **Test 2: Error Handling**
```bash
# Test duplicate email
curl -X POST http://localhost:8000/accounts/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User2"
  }'

# Test invalid credentials
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "WrongPassword"
  }'
```

### **Test 3: Token Management**
```bash
# 1. Signin to get tokens
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }')

# 2. Extract tokens (requires jq)
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.data.tokens.access_token')
REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.data.tokens.refresh_token')

# 3. Use access token for API calls
curl -X GET http://localhost:8000/accounts/api/dashboard/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 4. Refresh token
curl -X POST http://localhost:8000/accounts/api/refresh-token/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"

# 5. Logout
curl -X POST http://localhost:8000/accounts/api/logout/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

## 🔗 **Integration with ad_expert API**

### **Use JWT Token with ad_expert**
```bash
# 1. Get JWT token from signin
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/accounts/api/signin/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }')

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

# 2. Use token with ad_expert API
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for customer ID 9762343117?"
  }'
```

## 📝 **Notes**

- **Base URL**: `http://localhost:8000` (adjust for your environment)
- **Content-Type**: Always use `application/json` for POST requests
- **Authorization**: Use `Bearer TOKEN` format for protected endpoints
- **Token Expiry**: Access tokens expire, use refresh tokens to get new ones
- **Error Handling**: All endpoints return consistent error format
- **CORS**: Headers are set for cross-origin requests

## 🚀 **Quick Start**

1. **Signup**: Create a new user account
2. **Signin**: Get JWT tokens
3. **Use Tokens**: Access protected endpoints
4. **Refresh**: Get new access tokens when needed
5. **Logout**: Securely logout and blacklist tokens
