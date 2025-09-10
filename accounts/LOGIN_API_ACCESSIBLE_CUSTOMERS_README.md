# Login API with Accessible Customers

This document describes the updated login API endpoint that now includes accessible Google Ads customers in the response.

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

### **1. Successful Login - With Google OAuth Connected (Has Accessible Customers)**

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "2",
      "email": "user@example.com",
      "name": "John Doe",
      "provider": "email",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    },
    "google_oauth_connected": true,
    "accessible_customers": {
      "customers": [
        "customers/6295034578",
        "customers/8543230874",
        "customers/9631603999",
        "customers/5185115795"
      ],
      "total_count": 4,
      "last_updated": "2024-01-15T10:30:00.000Z",
      "raw_response": {
        "resourceNames": [
          "customers/6295034578",
          "customers/8543230874",
          "customers/9631603999",
          "customers/5185115795"
        ]
      }
    }
  }
}
```

### **2. Successful Login - With Google OAuth Connected (No Accessible Customers Saved)**

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "2",
      "email": "user@example.com",
      "name": "John Doe",
      "provider": "email",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    },
    "google_oauth_connected": true,
    "accessible_customers": null
  }
}
```

### **3. Successful Login - No Google OAuth Connected**

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "1",
      "email": "user@example.com",
      "name": "John Doe",
      "provider": "email",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    },
    "google_oauth_connected": false,
    "accessible_customers": null
  }
}
```

### **4. Invalid Credentials**

**Response (400):**
```json
{
  "success": false,
  "error": "Invalid username/email or password."
}
```

### **5. Missing Fields**

**Response (400):**
```json
{
  "success": false,
  "error": "Username/email and password are required."
}
```

## 🔄 **New Field Added**

### **`accessible_customers`**
- **Type**: `Object | null`
- **Description**: Contains accessible Google Ads customers data if user has Google OAuth connected and customers are saved
- **Structure**:
  ```json
  {
    "customers": ["customers/1234567890", "customers/0987654321"],
    "total_count": 2,
    "last_updated": "2024-01-15T10:30:00.000Z",
    "raw_response": {
      "resourceNames": ["customers/1234567890", "customers/0987654321"]
    }
  }
  ```

## 🧪 **Test Examples**

### **Test 1: Login with Accessible Customers**
```bash
curl -X POST 'http://localhost:8000/accounts/api/auth/login/' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://localhost:8080' \
  -H 'Pragma: no-cache' \
  -H 'Referer: http://localhost:8080/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36' \
  -H 'sec-ch-ua: "Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"' \
  -H 'sec-ch-ua-mobile: ?1' \
  -H 'sec-ch-ua-platform: "Android"' \
  --data-raw '{"email":"a@a.com","password":"a"}'
```

### **Test 2: Simple Login Test**
```bash
curl -X POST 'http://localhost:8000/accounts/api/auth/login/' \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"password123"}'
```

## 📊 **Response Field Details**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the login was successful |
| `message` | string | Human-readable message about the result |
| `data.user` | object | User information |
| `data.user.id` | string | User ID |
| `data.user.email` | string | User email address |
| `data.user.name` | string | User display name |
| `data.user.provider` | string | Authentication provider (always "email") |
| `data.user.created_at` | string | User creation timestamp (ISO 8601) |
| `data.user.updated_at` | string | User last update timestamp (ISO 8601) |
| `data.tokens` | object | JWT tokens for API authentication |
| `data.tokens.access_token` | string | JWT access token |
| `data.tokens.refresh_token` | string | JWT refresh token |
| `data.tokens.expires_in` | number | Token expiration time in seconds |
| `data.google_oauth_connected` | boolean | Whether user has Google OAuth connected |
| `data.accessible_customers` | object\|null | Accessible Google Ads customers data |

## 🔧 **Implementation Details**

### **When `accessible_customers` is included:**
1. User has an active Google OAuth connection (`google_oauth_connected: true`)
2. User has saved accessible customers in the database
3. The field contains the complete customer data with metadata

### **When `accessible_customers` is `null`:**
1. User has no Google OAuth connection (`google_oauth_connected: false`)
2. User has Google OAuth but no accessible customers saved
3. User has Google OAuth but the accessible customers data is empty

## 🚀 **Usage in Frontend**

```javascript
// Example frontend usage
fetch('/accounts/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    const { user, tokens, google_oauth_connected, accessible_customers } = data.data;
    
    // Store tokens for API calls
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    
    // Check if user has Google OAuth and accessible customers
    if (google_oauth_connected && accessible_customers) {
      console.log(`User has access to ${accessible_customers.total_count} Google Ads accounts:`);
      accessible_customers.customers.forEach(customer => {
        console.log(`  - ${customer}`);
      });
    } else if (google_oauth_connected) {
      console.log('User has Google OAuth but no accessible customers saved');
    } else {
      console.log('User needs to connect Google OAuth');
    }
  } else {
    console.error('Login failed:', data.error);
  }
});
```

## 🔄 **Backward Compatibility**

This update is **fully backward compatible**:
- Existing clients will continue to work without changes
- The new `accessible_customers` field is optional and can be safely ignored
- All existing response fields remain unchanged

## 🧪 **Testing**

Run the test script to verify functionality:

```bash
cd accounts
python test_login_with_accessible_customers.py
```

## 📝 **Notes**

1. **Performance**: The accessible customers data is retrieved from the database, so it's fast and doesn't require additional API calls
2. **Data Freshness**: The `last_updated` field shows when the customers data was last refreshed
3. **Security**: Only the authenticated user's accessible customers are returned
4. **Error Handling**: If there's an error retrieving accessible customers, the login still succeeds but `accessible_customers` will be `null`
