# Ad Expert API Testing Guide

## 🔧 Fixed API Authentication

The API now uses proper JWT authentication with DRF (Django REST Framework) instead of Django's session-based authentication. This ensures pure API responses without HTML templates.

## 🧪 Testing Steps

### Step 1: Test Authentication
First, test if your JWT token is working:

```bash
curl -X GET http://localhost:8000/ad-expert/api/test-auth/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "message": "Authentication successful",
  "user_id": 2,
  "username": "your_username",
  "is_authenticated": true,
  "timestamp": "2025-01-27T12:00:00.123456Z"
}
```

### Step 2: Test Chat Message Endpoint
Now test the chat message endpoint:

```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU2ODgzNzk1LCJpYXQiOjE3NTY4ODAxOTUsImp0aSI6ImFiN2QxMmI1ZTZhMDQ1YWQ5OTYxMmJiNzA5MmY0MmVhIiwidXNlcl9pZCI6Mn0.pNyt8b_QS-q279wjESRcyNoh_YgfQs-0Gzc__us1k9g" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me analyze my Google Ads performance?"
  }'
```

**Expected Response:**
```json
{
  "message_id": 1,
  "conversation_id": 1,
  "response": {
    "response_type": "text",
    "title": "Welcome to Ad Expert",
    "content": "Hello! I'm your AI advertising co-pilot. I can help you analyze your Google Ads and Meta Marketing campaigns. To get started, I'll need you to connect your accounts first.\n\nI can help you with:\n• Campaign performance analysis\n• CPA and ROI trends\n• Budget optimization recommendations\n• Cross-platform comparisons\n• Actionable insights and next steps\n\nWould you like to connect your Google Ads or Meta account to begin?",
    "data": [],
    "insights": [
      "Connect your Google Ads account for search campaign analysis",
      "Connect your Meta account for social media campaign insights"
    ]
  },
  "timestamp": "2025-01-27T12:00:00.123456Z"
}
```

## 🔍 Troubleshooting

### If you get HTML login template instead of JSON:

1. **Check JWT Token Validity:**
   ```bash
   # Test with a simple endpoint first
   curl -X GET http://localhost:8000/ad-expert/api/test-auth/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

2. **Verify Token Format:**
   - Make sure the token starts with `eyJ` (base64 encoded JWT header)
   - Ensure no extra spaces or characters
   - Check if token has expired

3. **Check Django Settings:**
   Make sure these are in your `settings.py`:
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework_simplejwt.authentication.JWTAuthentication',
           'rest_framework.authentication.SessionAuthentication',
       ],
       'DEFAULT_PERMISSION_CLASSES': [
           'rest_framework.permissions.IsAuthenticated',
       ],
   }
   ```

### If you get 401 Unauthorized:

1. **Token Expired:** Get a new JWT token
2. **Invalid Token:** Check token format and signing
3. **User Not Found:** Ensure the user exists in the database

### If you get 500 Internal Server Error:

1. **Check Django Logs:**
   ```bash
   python manage.py runserver --verbosity=2
   ```

2. **Verify Dependencies:**
   ```bash
   pip install djangorestframework djangorestframework-simplejwt
   ```

## 🚀 Complete Working Examples

### Example 1: Basic Chat
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for the last 14 days?"
  }'
```

### Example 2: With Conversation ID
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my top performing campaigns",
    "conversation_id": 1
  }'
```

### Example 3: Get Conversations
```bash
curl -X GET http://localhost:8000/ad-expert/api/conversations/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example 4: Health Check
```bash
curl -X GET http://localhost:8000/ad-expert/api/health/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔑 Getting a Valid JWT Token

If you need to get a new JWT token, you can use the existing authentication system:

### Option 1: Use Django Admin
1. Go to `http://localhost:8000/admin/`
2. Login with your credentials
3. Use the session-based authentication

### Option 2: Create a Token Endpoint
Add this to your `ad_expert/views.py` for testing:

```python
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Add user info to response
            user = request.user
            response.data['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        return response
```

Then add to URLs:
```python
path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
```

## 📝 Response Format

All successful API responses follow this format:

```json
{
  "message_id": 123,
  "conversation_id": 456,
  "response": {
    "response_type": "text|table|chart|action_items|etc",
    "title": "Response Title",
    "content": "Main content",
    "data": [...],
    "insights": [...]
  },
  "timestamp": "2025-01-27T12:00:00.123456Z"
}
```

## ✅ Success Indicators

- **200 OK:** Successful API call with JSON response
- **400 Bad Request:** Invalid request data (check message format)
- **401 Unauthorized:** Invalid or expired JWT token
- **500 Internal Server Error:** Server-side issue (check logs)

The API is now properly configured for React frontend integration with pure JSON responses and JWT authentication!

