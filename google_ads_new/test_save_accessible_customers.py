#!/usr/bin/env python3
"""
Test script for saving accessible customers to the database
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

def test_save_accessible_customers():
    """Test saving accessible customers to the database"""
    print("Testing save accessible customers functionality...")
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
        
        # Create a UserGoogleAuth record for the test user
        user_auth, auth_created = UserGoogleAuth.objects.get_or_create(
            user=user,
            google_user_id='test_google_user_123',
            defaults={
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token',
                'token_expiry': timezone.now() + timezone.timedelta(hours=1),
                'google_email': 'test@example.com',
                'google_name': 'Test User',
                'scopes': 'https://www.googleapis.com/auth/adwords',
                'is_active': True
            }
        )
        
        if auth_created:
            print("Created UserGoogleAuth record for test user")
        else:
            print("Using existing UserGoogleAuth record")
        
        # Login the user
        login_success = client.login(username='testuser', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return
        
        print("✅ Successfully logged in test user")
        
        # Test the list-accessible-customers endpoint (this will save to DB)
        print("\n1. Testing list-accessible-customers endpoint...")
        response = client.get('/google-ads-new/api/list-accessible-customers/')
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            if data.get('success') and data.get('saved_to_db'):
                print("✅ Successfully saved accessible customers to database")
            else:
                print("⚠️ API call succeeded but may not have saved to database")
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.content.decode()}")
        
        # Test the saved-accessible-customers endpoint
        print("\n2. Testing saved-accessible-customers endpoint...")
        response = client.get('/google-ads-new/api/saved-accessible-customers/')
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            print("✅ Successfully retrieved saved accessible customers from database")
        else:
            print(f"❌ Failed to retrieve saved customers with status {response.status_code}")
            print(f"Response: {response.content.decode()}")
        
        # Check the database directly
        print("\n3. Checking database directly...")
        user_auth.refresh_from_db()
        if user_auth.accessible_customers:
            print("✅ Accessible customers found in database:")
            print(f"  Customers: {user_auth.accessible_customers.get('customers', [])}")
            print(f"  Total count: {user_auth.accessible_customers.get('total_count', 0)}")
            print(f"  Last updated: {user_auth.accessible_customers.get('last_updated')}")
        else:
            print("❌ No accessible customers found in database")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

def test_database_structure():
    """Test the database structure and field"""
    print("\n" + "=" * 60)
    print("Testing database structure...")
    print("=" * 60)
    
    try:
        # Check if the field exists
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(accounts_usergoogleauth)")
        columns = cursor.fetchall()
        
        accessible_customers_field = None
        for column in columns:
            if column[1] == 'accessible_customers':
                accessible_customers_field = column
                break
        
        if accessible_customers_field:
            print("✅ accessible_customers field found in database")
            print(f"  Type: {accessible_customers_field[2]}")
            print(f"  Not null: {not accessible_customers_field[3]}")
            print(f"  Default: {accessible_customers_field[4]}")
        else:
            print("❌ accessible_customers field not found in database")
            
    except Exception as e:
        print(f"❌ Error checking database structure: {e}")

def show_curl_examples():
    """Show cURL examples for the new endpoints"""
    print("\n" + "=" * 60)
    print("cURL Examples")
    print("=" * 60)
    
    print("""
# 1. List accessible customers (saves to database)
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \\
  -H 'Authorization: Bearer <your_jwt_token>' \\
  -H 'Content-Type: application/json'

# 2. Get saved accessible customers from database
curl -X GET 'http://localhost:8000/google-ads-new/api/saved-accessible-customers/' \\
  -H 'Authorization: Bearer <your_jwt_token>' \\
  -H 'Content-Type: application/json'

# 3. Using session authentication
curl -X GET 'http://localhost:8000/google-ads-new/api/list-accessible-customers/' \\
  -H 'Cookie: sessionid=<your_session_id>' \\
  -H 'Content-Type: application/json'
""")

if __name__ == "__main__":
    print("Google Ads Accessible Customers Database Save Test")
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
    test_database_structure()
    test_save_accessible_customers()
    show_curl_examples()
    
    print("\n" + "=" * 60)
    print("Test completed!")
