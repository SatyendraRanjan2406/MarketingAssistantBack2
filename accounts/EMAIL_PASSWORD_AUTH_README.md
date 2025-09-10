# Email/Password Authentication API

## Overview

The accounts app now supports both **email/password authentication** and **Google OAuth authentication**. Users can sign up and sign in using traditional email/password credentials, with validation to prevent email conflicts between the two authentication methods.

## 🔐 **Authentication Methods**

### 1. **Email/Password Authentication**
- Traditional signup/signin with email and password
- JWT token-based authentication
- Email validation to prevent conflicts with Google OAuth

### 2. **Google OAuth Authentication**
- OAuth 2.0 flow with Google
- Automatic token refresh
- Integration with Google Ads API

## 📋 **API Endpoints**

### **Signup API**
```http
POST /accounts/api/signup/
```

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Acme Corp",
    "phone_number": "+1-555-123-4567",
    "address": "123 Main St, City, State"
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "Account created successfully!",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "company_name": "Acme Corp"
    },
    "google_account": {
        "is_connected": false,
        "accounts": [],
        "total_accounts": 0,
        "message": "No Google accounts connected"
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

**Error Response - Validation Errors (400):**
```json
{
    "success": false,
    "errors": {
        "email": ["This email address is already in use."],
        "username": ["A user with that username already exists."]
    }
}
```

### **Signin API**
```http
POST /accounts/api/signin/
```

**Request Body (Username):**
```json
{
    "username": "johndoe",
    "password": "SecurePass123"
}
```

**Request Body (Email):**
```json
{
    "email": "john@example.com",
    "password": "SecurePass123"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Login successful!",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "company_name": "Acme Corp"
    },
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

**Error Response (400):**
```json
{
    "success": false,
    "error": "Invalid username/email or password."
}
```

## 🧪 **Testing Examples**

### **1. Test Signup with Valid Data**
```bash
curl -X POST http://localhost:8000/accounts/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123",
    "first_name": "Test",
    "last_name": "User",
    "company_name": "Test Company"
  }'
```

### **2. Test Signup with Email Used for Google Auth**
```bash
# First, create a Google OAuth connection with email "googleuser@gmail.com"
# Then try to signup with the same email:
curl -X POST http://localhost:8000/accounts/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "googleuser@gmail.com",
    "password": "TestPass123",
    "first_name": "New",
    "last_name": "User"
  }'
```

**Expected Response:**
```json
{
    "success": false,
    "error": "Email used for google auth. use another email"
}
```

### **3. Test Signin with Username**
```bash
curl -X POST http://localhost:8000/accounts/api/signin/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123"
  }'
```

### **4. Test Signin with Email**
```bash
curl -X POST http://localhost:8000/accounts/api/signin/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### **5. Test Invalid Credentials**
```bash
curl -X POST http://localhost:8000/accounts/api/signin/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "WrongPassword"
  }'
```

**Expected Response:**
```json
{
    "success": false,
    "error": "Invalid username/email or password."
}
```

## 🔒 **Security Features**

### **Email Validation**
- ✅ **Unique email check**: Prevents duplicate emails in regular user accounts
- ✅ **Google OAuth conflict check**: Prevents using emails already registered with Google OAuth
- ✅ **Case-insensitive email matching**: Handles email case variations

### **Password Security**
- ✅ **Strong password requirements**: Minimum 8 characters with uppercase, lowercase, and numbers
- ✅ **Password confirmation**: Ensures password is entered correctly during signup
- ✅ **Secure password hashing**: Django's built-in password hashing

### **JWT Token Security**
- ✅ **Access tokens**: Short-lived tokens for API authentication
- ✅ **Refresh tokens**: Long-lived tokens for token renewal
- ✅ **Token blacklisting**: Secure logout by blacklisting refresh tokens

## 📊 **Database Models**

### **User Model (Django Built-in)**
- `id`: Primary key
- `username`: Unique username
- `email`: User's email address
- `first_name`: User's first name
- `last_name`: User's last name
- `password`: Hashed password
- `date_joined`: Account creation timestamp
- `is_active`: Account status

### **UserProfile Model**
- `user`: One-to-one relationship with User
- `company_name`: User's company
- `phone_number`: Contact phone number
- `address`: User's address
- `created_at`: Profile creation timestamp
- `updated_at`: Last profile update

### **UserGoogleAuth Model**
- `user`: Foreign key to User
- `google_email`: Google account email
- `access_token`: Google OAuth access token
- `refresh_token`: Google OAuth refresh token
- `token_expiry`: Token expiration time
- `is_active`: Connection status

## 🔄 **Authentication Flow**

### **Signup Flow**
1. User submits signup form with email/password
2. System validates email uniqueness (regular users + Google OAuth)
3. If valid, creates User and UserProfile records
4. Generates JWT tokens (access + refresh)
5. Returns success response with tokens

### **Signin Flow**
1. User submits credentials (username OR email + password)
2. System authenticates user
3. If valid, generates new JWT tokens
4. Returns success response with tokens and user info

### **Token Usage**
1. Client stores access token for API requests
2. Client uses refresh token to get new access tokens
3. Access tokens expire, refresh tokens can be renewed
4. Logout blacklists refresh token

## 🚀 **Integration with ad_expert API**

Once authenticated, users can use the JWT access token with the ad_expert API:

```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for customer ID 9762343117?"
  }'
```

## 📝 **Error Handling**

### **Common Error Scenarios**
1. **Email already used for Google OAuth**: Returns specific error message
2. **Email already used for regular signup**: Returns validation error
3. **Invalid credentials**: Returns authentication error
4. **Missing required fields**: Returns validation errors
5. **Weak password**: Returns password validation error

### **Error Response Format**
```json
{
    "success": false,
    "error": "Error message for single errors",
    "errors": {
        "field_name": ["Field-specific error messages"]
    }
}
```

## ✅ **Summary**

The accounts app now provides:

- ✅ **Email/Password Authentication**: Traditional signup/signin
- ✅ **Google OAuth Integration**: Seamless Google account connection
- ✅ **Email Conflict Prevention**: Prevents email conflicts between auth methods
- ✅ **JWT Token Security**: Secure token-based authentication
- ✅ **Flexible Signin**: Username or email-based login
- ✅ **Comprehensive Validation**: Strong input validation and error handling
- ✅ **Profile Management**: User profile with company and contact info
- ✅ **API Integration**: Ready for use with ad_expert and other APIs

The system is now ready for production use with both authentication methods working seamlessly together!

