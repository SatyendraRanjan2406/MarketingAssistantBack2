# Accessible Customers Database Storage

This document describes the functionality for saving and retrieving accessible Google Ads customers from the database.

## Overview

The `listAccessibleCustomers` API endpoint now automatically saves the accessible customers list to the `UserGoogleAuth` table in the database. This allows for:

1. **Persistent Storage**: Customers are saved and can be retrieved without making new API calls
2. **Performance**: Faster access to customer data without API latency
3. **Audit Trail**: Track when customers were last updated
4. **Offline Access**: Access customer data even when Google Ads API is unavailable

## Database Schema

### New Field Added to UserGoogleAuth Model

```python
accessible_customers = models.JSONField(
    blank=True, 
    null=True, 
    help_text="List of accessible Google Ads customer IDs"
)
```

### Data Structure

The `accessible_customers` field stores a JSON object with the following structure:

```json
{
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
```

## API Endpoints

### 1. List Accessible Customers (Saves to Database)

**Endpoint**: `GET /google-ads-new/api/list-accessible-customers/`

**Description**: Retrieves accessible customers from Google Ads API and saves them to the database.

**Authentication**: Required (JWT or Session)

**Response**:
```json
{
    "success": true,
    "customers": [
        "customers/6295034578",
        "customers/8543230874",
        "customers/9631603999",
        "customers/5185115795"
    ],
    "total_count": 4,
    "raw_response": {
        "resourceNames": [
            "customers/6295034578",
            "customers/8543230874",
            "customers/9631603999",
            "customers/5185115795"
        ]
    },
    "message": "Found 4 accessible customers",
    "saved_to_db": true
}
```

### 2. Get Saved Accessible Customers

**Endpoint**: `GET /google-ads-new/api/saved-accessible-customers/`

**Description**: Retrieves previously saved accessible customers from the database.

**Authentication**: Required (JWT or Session)

**Response**:
```json
{
    "success": true,
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
    },
    "message": "Retrieved 4 saved accessible customers"
}
```

## cURL Examples

### List and Save Accessible Customers

```bash
# Using JWT authentication
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Authorization: Bearer <your_jwt_token>' \
  -H 'Content-Type: application/json'

# Using session authentication
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \
  -H 'Cookie: sessionid=<your_session_id>' \
  -H 'Content-Type: application/json'
```

### Retrieve Saved Customers

```bash
# Using JWT authentication
curl -X GET 'http://localhost:8000/google-ads-new/api/saved-accessible-customers/' \
  -H 'Authorization: Bearer <your_jwt_token>' \
  -H 'Content-Type: application/json'

# Using session authentication
curl -X GET 'http://localhost:8000/google-ads-new/api/saved-accessible-customers/' \
  -H 'Cookie: sessionid=<your_session_id>' \
  -H 'Content-Type: application/json'
```

## Python Usage Examples

### Using the API Endpoints

```python
import requests

# List and save accessible customers
response = requests.get(
    'http://localhost:8000/google-ads-new/api/list-accessible-customers/',
    headers={'Authorization': 'Bearer your_jwt_token'}
)
data = response.json()
print(f"Found {data['total_count']} customers: {data['customers']}")

# Retrieve saved customers
response = requests.get(
    'http://localhost:8000/google-ads-new/api/saved-accessible-customers/',
    headers={'Authorization': 'Bearer your_jwt_token'}
)
data = response.json()
print(f"Retrieved {data['total_count']} saved customers")
```

### Direct Database Access

```python
from accounts.models import UserGoogleAuth
from django.contrib.auth.models import User

# Get user's accessible customers
user = User.objects.get(username='your_username')
user_auth = UserGoogleAuth.objects.filter(user=user, is_active=True).first()

if user_auth and user_auth.accessible_customers:
    customers = user_auth.accessible_customers['customers']
    total_count = user_auth.accessible_customers['total_count']
    last_updated = user_auth.accessible_customers['last_updated']
    
    print(f"User has access to {total_count} customers:")
    for customer in customers:
        print(f"  - {customer}")
else:
    print("No accessible customers found for this user")
```

## Error Handling

### Common Error Responses

1. **No Google Auth Record**:
```json
{
    "success": false,
    "error": "No active Google Auth record found. Please authenticate with Google first."
}
```

2. **No Saved Customers**:
```json
{
    "success": false,
    "error": "No accessible customers saved. Please call the list-accessible-customers endpoint first."
}
```

3. **Google Ads API Error**:
```json
{
    "success": false,
    "error": "No valid Google OAuth credentials found. Please authenticate with Google first."
}
```

## Database Migration

The new field was added via migration `0006_add_accessible_customers_field.py`:

```bash
# Apply the migration
python manage.py migrate

# Check migration status
python manage.py showmigrations accounts
```

## Testing

Run the test script to verify functionality:

```bash
cd google_ads_new
python test_save_accessible_customers.py
```

## Admin Interface

The `accessible_customers` field is visible in the Django admin interface under the "Google Ads" section of the `UserGoogleAuth` model.

## Performance Considerations

1. **Automatic Saving**: Customers are automatically saved on every API call
2. **No Duplicate Prevention**: Each API call overwrites the previous data
3. **JSON Storage**: Uses PostgreSQL JSONField for efficient storage and querying
4. **Error Resilience**: API calls succeed even if database saving fails

## Security Notes

1. **User Isolation**: Each user can only access their own saved customers
2. **Authentication Required**: All endpoints require valid authentication
3. **Data Privacy**: Customer IDs are stored securely in the database
4. **Token Management**: Uses existing OAuth token management system

## Future Enhancements

1. **Caching**: Add Redis caching for frequently accessed data
2. **Scheduling**: Automatic periodic updates of customer lists
3. **Notifications**: Alert when accessible customers change
4. **Analytics**: Track customer access patterns and usage
