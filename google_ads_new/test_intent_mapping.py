#!/usr/bin/env python3
"""
Test script for Intent Mapping API
Demonstrates mapping user queries to intent actions with date ranges and filters
"""

import requests
import json
import os
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/google-ads-new"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU3NDg2NDU0LCJpYXQiOjE3NTc0ODI4NTQsImp0aSI6IjljNTJlYzZkZjJkYTRhNThiYmM1YzZmNTYxODU5NzEwIiwidXNlcl9pZCI6IjE3In0.1NIGKsHNprfMrle8RZAgBwEAdtbDnrAYu6QZiS-gR1k"

def test_intent_mapping():
    """Test the intent mapping API with various queries"""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JWT_TOKEN}'
    }
    
    # Test queries with different complexity levels
    test_queries = [
        # Basic queries
        "Show me all campaigns",
        "Get campaigns with status active",
        "Show me ads for campaign 12345",
        "Get budget for campaign 67890",
        
        # Queries with date ranges
        "Show me campaigns from last 7 days",
        "Get performance data for this month",
        "Show me ads from yesterday",
        "Get budget data from last 30 days",
        
        # Queries with filters
        "Show me active campaigns with budget > $100",
        "Get campaigns containing 'summer' in the name",
        "Show me paused campaigns from last week",
        "Get ads with status enabled for campaign 12345",
        
        # Complex queries with multiple filters and date ranges
        "Show me active campaigns with budget > $500 from last 30 days",
        "Get performance data for campaigns containing 'holiday' from this month",
        "Show me ads with status enabled for campaign 12345 from last 7 days",
        "Get budget data for paused campaigns from yesterday",
        
        # Ad group (adset) queries
        "Show me ad groups for campaign 12345",
        "Get ad group 67890 details",
        "Show me ad groups with status active",
        "Get ad groups for campaign 12345 from last week",
        
        # Analysis queries
        "Compare campaign performance",
        "Show me trend analysis for clicks",
        "Analyze audience demographics",
        "Get performance summary with pie chart",
        
        # Creative queries
        "Generate ad copies for summer campaign",
        "Create creative ideas for Facebook ads",
        "Generate images for holiday promotion",
        
        # Optimization queries
        "Optimize campaign 12345",
        "Suggest budget allocation improvements",
        "Optimize ad group performance",
        
        # Technical queries
        "Check campaign consistency",
        "Audit duplicate keywords",
        "Check landing page compliance"
    ]
    
    print("🧪 Testing Intent Mapping API")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 40)
        
        try:
            # Test with authentication
            response = requests.post(
                f"{BASE_URL}/api/intent-mapping/",
                headers=headers,
                json={
                    "query": query,
                    "user_context": {
                        "customer_id": "1234567890",
                        "campaigns": ["12345", "67890"]
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Actions: {result.get('actions', [])}")
                    print(f"📅 Date Range: {result.get('date_range', {})}")
                    print(f"🔍 Filters: {len(result.get('filters', []))} filters")
                    print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
                    print(f"💭 Reasoning: {result.get('reasoning', '')[:100]}...")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Intent mapping tests completed!")

def test_available_actions():
    """Test getting available actions"""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JWT_TOKEN}'
    }
    
    print("\n🔍 Testing Available Actions API")
    print("=" * 50)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/intent-mapping/actions/",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Total Actions: {result.get('total_actions', 0)}")
                print(f"📊 Categories: {result.get('categories', {})}")
                
                # Show some sample actions
                actions = result.get('actions', [])
                print(f"\n📋 Sample Actions:")
                for action in actions[:5]:
                    print(f"  - {action['action']}: {action['description']}")
                print(f"  ... and {len(actions) - 5} more")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_actions_by_category():
    """Test getting actions by category"""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JWT_TOKEN}'
    }
    
    categories = ['basic_operations', 'analysis', 'creative', 'optimization']
    
    print("\n📂 Testing Actions by Category")
    print("=" * 50)
    
    for category in categories:
        try:
            response = requests.get(
                f"{BASE_URL}/api/intent-mapping/actions/{category}/",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ {category}: {result.get('count', 0)} actions")
                    print(f"   Actions: {result.get('actions', [])[:3]}...")
                else:
                    print(f"❌ {category}: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ {category}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {category}: Exception {e}")

def test_date_range_extraction():
    """Test date range extraction"""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JWT_TOKEN}'
    }
    
    date_queries = [
        "Show me data from last 7 days",
        "Get campaigns from this month",
        "Show me performance from yesterday",
        "Get data from last 30 days",
        "Show me results from today"
    ]
    
    print("\n📅 Testing Date Range Extraction")
    print("=" * 50)
    
    for query in date_queries:
        try:
            response = requests.post(
                f"{BASE_URL}/api/intent-mapping/extract-date-range/",
                headers=headers,
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    date_range = result.get('date_range', {})
                    print(f"✅ '{query}' -> {date_range}")
                else:
                    print(f"❌ '{query}': {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ '{query}': HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{query}': Exception {e}")

def test_without_auth():
    """Test the test endpoint (no auth required)"""
    
    print("\n🔓 Testing Without Authentication")
    print("=" * 50)
    
    test_query = "Show me active campaigns from last 7 days with budget > $100"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/intent-mapping/test/",
            json={"query": test_query}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Query: '{test_query}'")
                print(f"   Actions: {result.get('actions', [])}")
                print(f"   Date Range: {result.get('date_range', {})}")
                print(f"   Filters: {len(result.get('filters', []))} filters")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Run all tests"""
    print("🚀 Intent Mapping API Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/intent-mapping/actions/")
        if response.status_code != 200:
            print("❌ Server not running or endpoint not available")
            print("Please start the Django server: python manage.py runserver 8000")
            return
    except:
        print("❌ Cannot connect to server")
        print("Please start the Django server: python manage.py runserver 8000")
        return
    
    # Run tests
    test_intent_mapping()
    test_available_actions()
    test_actions_by_category()
    test_date_range_extraction()
    test_without_auth()
    
    print("\n🎉 All tests completed!")
    print("\n📝 Usage Examples:")
    print("1. Map query to intents:")
    print("   curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/' \\")
    print("        -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"query\": \"Show me active campaigns from last 7 days\"}'")
    print("\n2. Get available actions:")
    print("   curl -X GET 'http://localhost:8000/google-ads-new/api/intent-mapping/actions/' \\")
    print("        -H 'Authorization: Bearer YOUR_JWT_TOKEN'")
    print("\n3. Test without auth:")
    print("   curl -X POST 'http://localhost:8000/google-ads-new/api/intent-mapping/test/' \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"query\": \"Show me campaigns\"}'")

if __name__ == "__main__":
    main()

