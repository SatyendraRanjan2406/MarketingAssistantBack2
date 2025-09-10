# List Accessible Customers API - cURL Examples

This document provides cURL examples for the `list_accessible_customers` API endpoint.

## API Endpoint

**URL**: `GET /google-ads-new/api/list-accessible-customers/`

## Authentication Methods

### 1. Session Authentication (Django Default)

```bash
# First, login to get session cookie
curl -X POST 'http://localhost:8000/accounts/login/' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# Then use the session cookie for the API call
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Cookie: sessionid=<session_id_from_login>' \
  -H 'Content-Type: application/json'
```

### 2. JWT Authentication (if configured)

```bash
# First, get JWT token
curl -X POST 'http://localhost:8000/accounts/api/token/' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# Then use the JWT token for the API call
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json'
```

### 3. One-liner with Session Authentication

```bash
# Login and get session cookie in one command
SESSION_ID=$(curl -s -X POST 'http://localhost:8000/accounts/login/' \
  -H 'Content-Type: application/json' \
  -d '{"username": "your_username", "password": "your_password"}' \
  -c - | grep sessionid | cut -f7)

# Use the session cookie
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H "Cookie: sessionid=$SESSION_ID" \
  -H 'Content-Type: application/json'
```

## Expected Responses

### Success Response

```json
{
  "success": true,
  "customers": [
    "customers/1234567890",
    "customers/0987654321"
  ],
  "total_count": 2,
  "raw_response": {
    "resourceNames": [
      "customers/1234567890",
      "customers/0987654321"
    ]
  },
  "message": "Found 2 accessible customers"
}
```

### Error Response (No Authentication)

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Error Response (Invalid Credentials)

```json
{
  "success": false,
  "error": "No valid Google OAuth credentials found. Please authenticate with Google first."
}
```

### Error Response (Missing Developer Token)

```json
{
  "success": false,
  "error": "Developer token not configured in environment variables"
}
```

## Testing with Different Scenarios

### 1. Test with Valid User

```bash
# Replace with your actual credentials
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Cookie: sessionid=your_session_id' \
  -H 'Content-Type: application/json' \
  -v
```

### 2. Test Error Handling

```bash
# Test without authentication
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Content-Type: application/json' \
  -v

# Test with invalid session
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Cookie: sessionid=invalid_session_id' \
  -H 'Content-Type: application/json' \
  -v
```

### 3. Test with Different HTTP Methods

```bash
# Test POST (should return 405 Method Not Allowed)
curl -X POST 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Cookie: sessionid=your_session_id' \
  -H 'Content-Type: application/json' \
  -v

# Test PUT (should return 405 Method Not Allowed)
curl -X PUT 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Cookie: sessionid=your_session_id' \
  -H 'Content-Type: application/json' \
  -v
```

## Production Examples

### Using HTTPS

```bash
curl -X GET 'https://yourdomain.com/google-ads-new/api/list-accessible-customers/' \
  -H 'Authorization: Bearer your_jwt_token' \
  -H 'Content-Type: application/json'
```

### With Additional Headers

```bash
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Cookie: sessionid=your_session_id' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'User-Agent: MyApp/1.0' \
  -v
```

## Python Requests Example

```python
import requests

# Using session authentication
session = requests.Session()
login_response = session.post('http://localhost:8000/accounts/login/', json={
    'username': 'your_username',
    'password': 'your_password'
})

if login_response.status_code == 200:
    api_response = session.get('http://localhost:8000/google-ads-new/api/list-accessible-customers/')
    print(api_response.json())
```

## JavaScript Fetch Example

```javascript
// Using session authentication
fetch('http://localhost:8000/google-ads-new/api/list-accessible-customers/', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'Cookie': 'sessionid=your_session_id'
    },
    credentials: 'include'
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check if you're properly authenticated
2. **403 Forbidden**: Check if your user has the required permissions
3. **500 Internal Server Error**: Check server logs and environment variables
4. **Connection Refused**: Make sure the Django server is running

### Debug Commands

```bash
# Check if the server is running
curl -I http://localhost:8000/

# Check if the endpoint exists
curl -I http://localhost:8000/google-ads-new/api/list-accessible-customers/

# Check with verbose output
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Cookie: sessionid=your_session_id' \
  -H 'Content-Type: application/json' \
  -v --trace-ascii debug.log
```
