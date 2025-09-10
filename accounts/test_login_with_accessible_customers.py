#!/usr/bin/env python3
"""
Test script for login API with accessible customers
"""

import os
import sys
import django
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from accounts.models import UserGoogleAuth
from django.utils import timezone

def test_login_with_accessible_customers():
    """Test login API with accessible customers in response"""
    print("Testing login API with accessible customers...")
    print("=" * 60)
    
    try:
        # Create a test client
        client = Client()
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='a@a.com',
            defaults={
                'email': 'a@a.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('a')
            user.save()
            print(f"Created test user: {user.username}")
        else:
            print(f"Using existing test user: {user.username}")
        
        # Create a UserGoogleAuth record with accessible customers
        user_auth, auth_created = UserGoogleAuth.objects.get_or_create(
            user=user,
            google_user_id='test_google_user_123',
            defaults={
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token',
                'token_expiry': timezone.now() + timezone.timedelta(hours=1),
                'google_email': 'a@a.com',
                'google_name': 'Test User',
                'scopes': 'https://www.googleapis.com/auth/adwords',
                'is_active': True,
                'accessible_customers': {
                    'customers': [
                        'customers/6295034578',
                        'customers/8543230874',
                        'customers/9631603999',
                        'customers/5185115795'
                    ],
                    'total_count': 4,
                    'last_updated': timezone.now().isoformat(),
                    'raw_response': {
                        'resourceNames': [
                            'customers/6295034578',
                            'customers/8543230874',
                            'customers/9631603999',
                            'customers/5185115795'
                        ]
                    }
                }
            }
        )
        
        if auth_created:
            print("Created UserGoogleAuth record with accessible customers")
        else:
            # Update existing record with accessible customers
            user_auth.accessible_customers = {
                'customers': [
                    'customers/6295034578',
                    'customers/8543230874',
                    'customers/9631603999',
                    'customers/5185115795'
                ],
                'total_count': 4,
                'last_updated': timezone.now().isoformat(),
                'raw_response': {
                    'resourceNames': [
                        'customers/6295034578',
                        'customers/8543230874',
                        'customers/9631603999',
                        'customers/5185115795'
                    ]
                }
            }
            user_auth.save()
            print("Updated UserGoogleAuth record with accessible customers")
        
        # Test the login endpoint
        print("\n1. Testing login endpoint...")
        response = client.post(
            '/accounts/api/auth/login/',
            data=json.dumps({
                'email': 'a@a.com',
                'password': 'a'
            }),
            content_type='application/json'
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            # Check if accessible_customers is in the response
            if 'accessible_customers' in data.get('data', {}):
                accessible_customers = data['data']['accessible_customers']
                if accessible_customers:
                    print(f"\n✅ Accessible customers found in response:")
                    print(f"  Total count: {accessible_customers.get('total_count', 0)}")
                    print(f"  Customers: {accessible_customers.get('customers', [])}")
                    print(f"  Last updated: {accessible_customers.get('last_updated')}")
                else:
                    print("\n⚠️ accessible_customers is null in response")
            else:
                print("\n❌ accessible_customers not found in response")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Response: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

def test_login_without_google_oauth():
    """Test login API without Google OAuth connection"""
    print("\n" + "=" * 60)
    print("Testing login API without Google OAuth...")
    print("=" * 60)
    
    try:
        client = Client()
        
        # Create a user without Google OAuth
        user, created = User.objects.get_or_create(
            username='nooauth@test.com',
            defaults={
                'email': 'nooauth@test.com',
                'first_name': 'No',
                'last_name': 'OAuth'
            }
        )
        
        if created:
            user.set_password('testpass')
            user.save()
            print(f"Created test user without Google OAuth: {user.username}")
        
        # Test the login endpoint
        response = client.post(
            '/accounts/api/auth/login/',
            data=json.dumps({
                'email': 'nooauth@test.com',
                'password': 'testpass'
            }),
            content_type='application/json'
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            
            # Check accessible_customers should be null
            accessible_customers = data.get('data', {}).get('accessible_customers')
            if accessible_customers is None:
                print("✅ accessible_customers is null (as expected for no Google OAuth)")
            else:
                print(f"⚠️ accessible_customers is not null: {accessible_customers}")
                
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Response: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def show_curl_example():
    """Show cURL example for the login endpoint"""
    print("\n" + "=" * 60)
    print("cURL Example")
    print("=" * 60)
    
    print("""
# Login with accessible customers in response
curl -X POST 'http://localhost:8000/accounts/api/auth/login/' \\
  -H 'Accept: */*' \\
  -H 'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8' \\
  -H 'Cache-Control: no-cache' \\
  -H 'Connection: keep-alive' \\
  -H 'Content-Type: application/json' \\
  -H 'Origin: http://localhost:8080' \\
  -H 'Pragma: no-cache' \\
  -H 'Referer: http://localhost:8080/' \\
  -H 'Sec-Fetch-Dest: empty' \\
  -H 'Sec-Fetch-Mode: cors' \\
  -H 'Sec-Fetch-Site: same-site' \\
  -H 'User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36' \\
  -H 'sec-ch-ua: "Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"' \\
  -H 'sec-ch-ua-mobile: ?1' \\
  -H 'sec-ch-ua-platform: "Android"' \\
  --data-raw '{"email":"a@a.com","password":"a"}'

# Expected response with accessible customers:
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "1",
      "email": "a@a.com",
      "name": "Test User",
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
""")

if __name__ == "__main__":
    print("Login API with Accessible Customers Test")
    print("=" * 60)
    
    # Run tests
    test_login_with_accessible_customers()
    test_login_without_google_oauth()
    show_curl_example()
    
    print("\n" + "=" * 60)
    print("Test completed!")
