# Login API with Google OAuth Connection Flag

## 🎯 **Updated API Endpoint**
```http
POST /accounts/api/auth/login/
```

## 🔐 **Authentication**
- ✅ **No Authentication Required**: This is a login endpoint

## 📤 **Request Format**
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

## 📥 **Response Formats**

### **1. Successful Login - No Google OAuth Connected**

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "10",
      "email": "testuser@example.com",
      "name": "Test User",
      "provider": "email",
      "created_at": "2025-09-03T10:06:24.052150+00:00Z",
      "updated_at": "2025-09-03T10:06:24.052150+00:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    },
    "google_oauth_connected": false
  }
}
```

### **2. Successful Login - Google OAuth Connected**

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "2",
      "email": "jon@gmail.com",
      "name": "Jon Jon",
      "provider": "email",
      "created_at": "2025-08-20T12:56:09.939430+00:00Z",
      "updated_at": "2025-08-20T12:56:09.939430+00:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    },
    "google_oauth_connected": true
  }
}
```

### **3. Invalid Credentials**

**Response (400):**
```json
{
  "success": false,
  "error": "Invalid username/email or password."
}
```

### **4. Missing Fields**

**Response (400):**
```json
{
  "success": false,
  "error": "Username/email and password are required."
}
```

### **5. Server Error**

**Response (500):**
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

## 🧪 **Test Examples**

### **Test 1: Login with Google OAuth Connected**
```bash
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jon@gmail.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "2",
      "email": "jon@gmail.com",
      "name": "Jon Jon",
      "provider": "email",
      "created_at": "2025-08-20T12:56:09.939430+00:00Z",
      "updated_at": "2025-08-20T12:56:09.939430+00:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    },
    "google_oauth_connected": true
  }
}
```

### **Test 2: Login without Google OAuth**
```bash
curl -X POST http://localhost:8000/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "10",
      "email": "testuser@example.com",
      "name": "Test User",
      "provider": "email",
      "created_at": "2025-09-03T10:06:24.052150+00:00Z",
      "updated_at": "2025-09-03T10:06:24.052150+00:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    },
    "google_oauth_connected": false
  }
}
```

### **Test 3: Production URL**
```bash
curl -X POST https://your-api-domain.com/accounts/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

## 🔄 **API Logic Flow**

### **Step 1: Input Validation**
```python
email = request.data.get('email')
password = request.data.get('password')

if not email or not password:
    return Response({
        'success': False,
        'error': 'Username/email and password are required.'
    }, status=400)
```

### **Step 2: User Authentication**
```python
# Try to authenticate with email
user = authenticate(request, username=email, password=password)

# If email authentication fails, try username authentication
if user is None:
    try:
        user_obj = User.objects.get(email=email)
        user = authenticate(request, username=user_obj.username, password=password)
    except User.DoesNotExist:
        pass
```

### **Step 3: Google OAuth Check**
```python
# Check if user has Google OAuth connection
auth_service = UserGoogleAuthService()
google_auth_record = auth_service.get_valid_auth(user)
has_google_oauth = google_auth_record is not None
```

### **Step 4: Response Generation**
```python
response_data = {
    'success': True,
    'message': 'Login successful',
    'data': {
        'user': { ... },
        'tokens': { ... },
        'google_oauth_connected': has_google_oauth  # NEW FLAG
    }
}
```

## 🎯 **New Feature: Google OAuth Connection Flag**

### **What is `google_oauth_connected`?**
- **Type**: Boolean
- **Purpose**: Indicates whether the user has an active Google OAuth connection
- **Values**:
  - `true`: User has valid Google OAuth tokens stored
  - `false`: User has no Google OAuth connection

### **How It's Determined**
```python
# Check if user has Google OAuth connection
auth_service = UserGoogleAuthService()
google_auth_record = auth_service.get_valid_auth(user)
has_google_oauth = google_auth_record is not None
```

### **Frontend Usage**
```javascript
async function handleLogin(email, password) {
  try {
    const response = await fetch('/accounts/api/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Store tokens
      localStorage.setItem('access_token', data.data.tokens.access_token);
      localStorage.setItem('refresh_token', data.data.tokens.refresh_token);
      
      // Check Google OAuth status
      if (data.data.google_oauth_connected) {
        console.log('User has Google OAuth connected');
        // Show Google Ads features
        showGoogleAdsFeatures();
      } else {
        console.log('User needs to connect Google OAuth');
        // Show "Connect Google Account" button
        showGoogleOAuthButton();
      }
      
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } else {
      console.error('Login failed:', data.error);
    }
  } catch (error) {
    console.error('Login error:', error);
  }
}
```

### **React Component Integration**
```jsx
import { useState } from 'react';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('/accounts/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: email,
          password: password
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Store tokens
        localStorage.setItem('access_token', data.data.tokens.access_token);
        localStorage.setItem('refresh_token', data.data.tokens.refresh_token);
        
        // Check Google OAuth status
        if (data.data.google_oauth_connected) {
          // User can access Google Ads features immediately
          console.log('Google OAuth connected:', data.data.user.email);
        } else {
          // User needs to connect Google OAuth
          console.log('Google OAuth not connected');
        }
        
        // Redirect or update UI
        window.location.href = '/dashboard';
      } else {
        alert('Login failed: ' + data.error);
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

## 🔗 **Integration with Other APIs**

### **1. Use with Google OAuth Connect API**
```javascript
async function checkGoogleConnectionAfterLogin() {
  const loginResponse = await fetch('/accounts/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const loginData = await loginResponse.json();
  
  if (loginData.success) {
    if (loginData.data.google_oauth_connected) {
      // User already has Google OAuth, can use ad_expert API
      console.log('Ready to use Google Ads features');
    } else {
      // User needs to connect Google OAuth
      console.log('Need to connect Google OAuth');
    }
  }
}
```

### **2. Use with ad_expert API**
```javascript
async function useAdExpertAPI() {
  // First login
  const loginResponse = await fetch('/accounts/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const loginData = await loginResponse.json();
  
  if (loginData.success && loginData.data.google_oauth_connected) {
    // Use ad_expert API
    const chatResponse = await fetch('/ad-expert/api/chat/message/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${loginData.data.tokens.access_token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: "What is my CPA trend for Google Ads?"
      })
    });
    
    return await chatResponse.json();
  } else {
    throw new Error('Google OAuth connection required');
  }
}
```

## 📊 **Response Field Descriptions**

### **Success Response Fields:**
- **`success`**: Boolean indicating API call success
- **`message`**: Human-readable success message
- **`data`**: Main response data object
  - **`user`**: User information
    - **`id`**: User ID (string)
    - **`email`**: User's email address
    - **`name`**: User's full name
    - **`provider`**: Authentication provider ("email")
    - **`created_at`**: Account creation timestamp (ISO format)
    - **`updated_at`**: Last update timestamp (ISO format)
  - **`tokens`**: JWT tokens
    - **`access_token`**: JWT access token
    - **`refresh_token`**: JWT refresh token
    - **`expires_in`**: Token expiry time in seconds (3600)
  - **`google_oauth_connected`**: **NEW** - Boolean indicating Google OAuth status

### **Error Response Fields:**
- **`success`**: Boolean indicating API call failure
- **`error`**: Error message describing the issue

## ⚠️ **Important Notes**

1. **Google OAuth Check**: The flag is determined by checking for valid Google OAuth tokens in the database
2. **Token Validation**: Only active, non-expired Google OAuth tokens are considered
3. **Real-time Status**: The flag reflects the current state at login time
4. **Frontend Integration**: Use this flag to show/hide Google Ads features
5. **Security**: JWT tokens are required for subsequent API calls

## 🎯 **Summary**

The updated login API now includes:

- ✅ **Google OAuth connection flag** (`google_oauth_connected`)
- ✅ **Real-time OAuth status** check during login
- ✅ **Frontend-friendly boolean** for easy UI decisions
- ✅ **Consistent response format** with nested data structure
- ✅ **JWT token generation** for authenticated requests
- ✅ **Comprehensive error handling** with proper status codes

**Perfect for frontend applications that need to know Google OAuth status immediately after login!** 🚀

