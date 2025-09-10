#!/usr/bin/env python3
"""
Test script for the list_accessible_customers API endpoint
"""

import os
import sys
import django
import requests
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_api_endpoint():
    """Test the API endpoint directly"""
    print("Testing list_accessible_customers API endpoint...")
    print("=" * 60)
    
    try:
        # Create a test client
        client = Client()
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"Created test user: {user.username}")
        else:
            print(f"Using existing test user: {user.username}")
        
        # Login the user
        login_success = client.login(username='testuser', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return
        
        print("✅ Successfully logged in test user")
        
        # Make the API call
        response = client.get('/google-ads-new/api/list-accessible-customers/')
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API endpoint working correctly")
                print(f"Found {data.get('total_count', 0)} accessible customers")
                print(f"Customers: {data.get('customers', [])}")
            else:
                print(f"❌ API returned error: {data.get('error')}")
        else:
            print(f"❌ API returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def generate_curl_command():
    """Generate cURL command for the API endpoint"""
    print("\n" + "=" * 60)
    print("cURL Command for list_accessible_customers API")
    print("=" * 60)
    
    # Note: In a real scenario, you would need to get the actual session cookie or JWT token
    print("""
# Method 1: Using session authentication (after login)
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \\
  -H 'Cookie: sessionid=<your_session_id>' \\
  -H 'Content-Type: application/json'

# Method 2: Using JWT authentication (if configured)
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \\
  -H 'Authorization: Bearer <your_jwt_token>' \\
  -H 'Content-Type: application/json'

# Method 3: Using Django's test client (for testing)
python manage.py shell
>>> from django.test import Client
>>> client = Client()
>>> client.login(username='your_username', password='your_password')
>>> response = client.get('/google-ads-new/api/list-accessible-customers/')
>>> print(response.json())
""")

def show_api_documentation():
    """Show API documentation"""
    print("\n" + "=" * 60)
    print("API Documentation")
    print("=" * 60)
    
    print("""
Endpoint: GET /google-ads-new/api/list-accessible-customers/

Description: Get list of accessible Google Ads customers for the authenticated user

Authentication: Required (Session or JWT)

Headers:
  - Content-Type: application/json
  - Cookie: sessionid=<session_id> (for session auth)
  - Authorization: Bearer <jwt_token> (for JWT auth)

Response Format:
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

Error Response:
{
  "success": false,
  "error": "Error message describing what went wrong"
}

Status Codes:
  - 200: Success
  - 400: Bad Request (authentication or API error)
  - 401: Unauthorized (not authenticated)
  - 500: Internal Server Error
""")

if __name__ == "__main__":
    print("Google Ads listAccessibleCustomers API Endpoint Test")
    print("=" * 60)
    
    # Check if we have the required environment variables
    developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
    if not developer_token:
        print("❌ GOOGLE_ADS_DEVELOPER_TOKEN not set in environment")
        print("Please set your Google Ads developer token in the environment")
        print("The API will still work but may return authentication errors")
    else:
        print(f"✅ Developer token found: {developer_token[:10]}...")
    
    # Run tests
    test_api_endpoint()
    generate_curl_command()
    show_api_documentation()
    
    print("\n" + "=" * 60)
    print("Test completed!")
