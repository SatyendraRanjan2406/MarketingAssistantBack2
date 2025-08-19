# Google Ads Account Access API

This document describes the Google Ads Account Access API endpoints for programmatically requesting access to other Google Ads accounts using the **Google Ads API v28.0.0**.

## Overview

The API allows you to:
1. **Request access** to another Google Ads account (creates a pending invitation)
2. **Check pending requests** for account access
3. **Use direct function calls** for programmatic access

## API Endpoints

### 1. Request Account Access

**Endpoint:** `POST /google-ads-new/api/request-account-access/`

**Purpose:** Send a request to access another Google Ads account

**Request Body:**
```json
{
    "manager_customer_id": "6077394633",
    "client_customer_id": "9999999999"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Link request sent successfully",
    "resource_name": "customers/6077394633/customerClientLinks/123456789",
    "manager_customer_id": "6077394633",
    "client_customer_id": "9999999999"
}
```

### 2. Get Pending Access Requests

**Endpoint:** `GET /google-ads-new/api/pending-access-requests/?manager_customer_id=6077394633`

**Purpose:** Retrieve all pending access requests for a manager account

**Response:**
```json
{
    "success": true,
    "pending_requests": [
        {
            "client_customer": "customers/9999999999",
            "manager_link_id": "123456789",
            "status": "PENDING",
            "pending_manager_link_invitation": true
        }
    ],
    "manager_customer_id": "6077394633"
}
```

## Direct Function Usage

You can also use the `send_link_request` function directly in your Python code:

```python
from google_ads_new.google_ads_api_service import send_link_request

# Send a link request
result = send_link_request(
    manager_customer_id="6077394633",
    client_customer_id="9999999999"
)

print(result)
```

## cURL Examples

### Request Account Access
```bash
curl -X POST http://localhost:8000/google-ads-new/api/request-account-access/ \
  -H "Content-Type: application/json" \
  -d '{
    "manager_customer_id": "6077394633",
    "client_customer_id": "9999999999"
  }'
```

### Get Pending Requests
```bash
curl -X GET "http://localhost:8000/google-ads-new/api/pending-access-requests/?manager_customer_id=6077394633"
```

## Python Examples

### Using the API endpoint
```python
import requests

url = "http://localhost:8000/google-ads-new/api/request-account-access/"
payload = {
    "manager_customer_id": "6077394633",
    "client_customer_id": "9999999999"
}

response = requests.post(url, json=payload)
print(response.json())
```

### Using the direct function
```python
from google_ads_new.google_ads_api_service import send_link_request

result = send_link_request("6077394633", "9999999999")
print(result)
```

## Configuration

Make sure your `google-ads.yaml` file is properly configured:

```yaml
developer_token: YOUR_DEVELOPER_TOKEN
# This should be your MANAGER ACCOUNT (MCC) ID, not a client account ID
login_customer_id: 6077394633
client_id: YOUR_CLIENT_ID
client_secret: YOUR_CLIENT_SECRET
refresh_token: YOUR_REFRESH_TOKEN
use_proto_plus: true
```

## Authentication

**For Testing:** The endpoints are currently CSRF-free and authentication-free for development purposes.

**For Production:** Re-enable authentication and user validation in the views.

## Error Handling

The API provides detailed error messages for common issues:

- **Permission Denied:** Check your manager account permissions
- **Developer Token Not Approved:** Upgrade to Basic/Standard access
- **Invalid Customer ID:** Verify the customer ID format and existence

## Testing

Run the test suite to verify everything is working:

```bash
python google_ads_new/test_account_access_api.py
```

## Requirements

- Google Ads API v28.0.0
- Django 5.2+
- Python 3.12+
- Valid Google Ads developer token
- OAuth2 credentials

## Notes

- **Manager Account Required:** You must have a Google Ads Manager Account (MCC)
- **Developer Token:** Must be approved for Basic or Standard access (not just Test)
- **Customer IDs:** Must be valid 10-digit Google Ads customer IDs
- **API Version:** Uses the latest Google Ads API v28.0.0 structure

## Troubleshooting

1. **"Failed to initialize Google Ads API client"**: Check your `google-ads.yaml` configuration
2. **"USER_PERMISSION_DENIED"**: Verify your `login_customer_id` is your manager account
3. **"DEVELOPER_TOKEN_NOT_APPROVED"**: Upgrade your developer token access level
4. **Import errors**: Ensure you have `google-ads==28.0.0` installed
