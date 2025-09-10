# Google Ads listAccessibleCustomers API Wrapper

This document describes the wrapper functions for the Google Ads API `listAccessibleCustomers` endpoint.

## Overview

The `listAccessibleCustomers` API endpoint allows you to retrieve a list of all Google Ads customer accounts that the authenticated user has access to. This is useful for discovering which accounts you can manage through the Google Ads API.

## API Endpoint

- **URL**: `https://googleads.googleapis.com/v21/customers:listAccessibleCustomers`
- **Method**: GET
- **Headers**: 
  - `Authorization: Bearer <access_token>`
  - `developer-token: <developer_token>`

## Wrapper Functions

### 1. Standalone Function

```python
from google_ads_new.google_ads_api_service import list_accessible_customers

# List accessible customers for the first user in the system
result = list_accessible_customers()

# List accessible customers for a specific user
result = list_accessible_customers(user_id=1)

if result['success']:
    print(f"Found {result['total_count']} accessible customers")
    for customer in result['customers']:
        print(f"Customer: {customer}")
else:
    print(f"Error: {result['error']}")
```

### 2. Class Method

```python
from google_ads_new.google_ads_api_service import GoogleAdsAPIService

# Create service instance
api_service = GoogleAdsAPIService(user_id=1)

# List accessible customers
result = api_service.list_accessible_customers()

if result['success']:
    print(f"Found {result['total_count']} accessible customers")
    for customer in result['customers']:
        print(f"Customer: {customer}")
else:
    print(f"Error: {result['error']}")
```

## Response Format

The wrapper functions return a dictionary with the following structure:

```python
{
    'success': True,  # Boolean indicating if the request was successful
    'customers': [    # List of customer resource names
        'customers/1234567890',
        'customers/0987654321'
    ],
    'total_count': 2,  # Number of accessible customers
    'raw_response': {  # Complete API response
        'resourceNames': [
            'customers/1234567890',
            'customers/0987654321'
        ]
    }
}
```

## Error Handling

The functions handle various error conditions:

- **No valid access token**: User needs to authenticate with Google OAuth
- **Developer token not configured**: `GOOGLE_ADS_DEVELOPER_TOKEN` environment variable not set
- **HTTP request errors**: Network issues or API errors
- **User not found**: Invalid user ID provided

## Prerequisites

1. **Google OAuth Setup**: User must have authenticated with Google OAuth
2. **Developer Token**: `GOOGLE_ADS_DEVELOPER_TOKEN` environment variable must be set
3. **Django Setup**: Django must be properly configured and running

## Testing

Run the test script to verify the wrapper functions work correctly:

```bash
cd google_ads_new
python test_list_accessible_customers.py
```

## cURL Equivalent

The wrapper functions are equivalent to this cURL command:

```bash
curl --location 'https://googleads.googleapis.com/v21/customers:listAccessibleCustomers' \
--header 'Authorization: Bearer <access_token>' \
--header 'developer-token: <developer_token>'
```

## Usage in Views

You can use these functions in Django views:

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from google_ads_new.google_ads_api_service import list_accessible_customers

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accessible_customers_view(request):
    """Get accessible customers for the authenticated user"""
    result = list_accessible_customers(user_id=request.user.id)
    return Response(result)
```

## Notes

- The API uses Google Ads API v21
- Access tokens are automatically refreshed if needed
- The functions handle both success and error cases gracefully
- All API calls are logged for debugging purposes
