#!/usr/bin/env python3
"""
Test script for Google Ads API documentation constants
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from google_ads_new.constants import (
    GOOGLE_ADS_API_DOCS_URLS,
    GOOGLE_ADS_DOCS_CATEGORIES,
    GOOGLE_ADS_DOCS_QUICK_ACCESS
)

def test_constants():
    """Test the Google Ads API documentation constants"""
    print("Google Ads API Documentation Constants Test")
    print("=" * 60)
    
    # Test basic list access
    print(f"Total documentation URLs: {len(GOOGLE_ADS_API_DOCS_URLS)}")
    print(f"First URL: {GOOGLE_ADS_API_DOCS_URLS[0]}")
    print(f"Last URL: {GOOGLE_ADS_API_DOCS_URLS[-1]}")
    
    # Test categorized access
    print(f"\nCategorized documentation:")
    print(f"Release notes: {GOOGLE_ADS_DOCS_CATEGORIES['release_notes']}")
    print(f"Getting started: {GOOGLE_ADS_DOCS_CATEGORIES['get_started']['introduction']}")
    print(f"OAuth overview: {GOOGLE_ADS_DOCS_CATEGORIES['oauth']['overview']}")
    print(f"Account management: {GOOGLE_ADS_DOCS_CATEGORIES['account_management']['overview']}")
    
    # Test quick access
    print(f"\nQuick access URLs:")
    for key, url in GOOGLE_ADS_DOCS_QUICK_ACCESS.items():
        print(f"  {key}: {url}")
    
    # Test specific categories
    print(f"\nGet Started URLs:")
    for key, url in GOOGLE_ADS_DOCS_CATEGORIES['get_started'].items():
        print(f"  {key}: {url}")
    
    print(f"\nOAuth URLs:")
    for key, url in GOOGLE_ADS_DOCS_CATEGORIES['oauth'].items():
        print(f"  {key}: {url}")
    
    print(f"\nConcepts URLs:")
    for key, url in GOOGLE_ADS_DOCS_CATEGORIES['concepts'].items():
        print(f"  {key}: {url}")
    
    print(f"\nAccount Management URLs:")
    for key, url in GOOGLE_ADS_DOCS_CATEGORIES['account_management'].items():
        print(f"  {key}: {url}")

def show_usage_examples():
    """Show usage examples for the constants"""
    print("\n" + "=" * 60)
    print("Usage Examples")
    print("=" * 60)
    
    print("""
# Import the constants
from google_ads_new.constants import (
    GOOGLE_ADS_API_DOCS_URLS,
    GOOGLE_ADS_DOCS_CATEGORIES,
    GOOGLE_ADS_DOCS_QUICK_ACCESS
)

# Access all URLs
all_urls = GOOGLE_ADS_API_DOCS_URLS
print(f"Total URLs: {len(all_urls)}")

# Access specific categories
oauth_overview = GOOGLE_ADS_DOCS_CATEGORIES['oauth']['overview']
getting_started = GOOGLE_ADS_DOCS_CATEGORIES['get_started']['introduction']

# Quick access to common URLs
dev_token_setup = GOOGLE_ADS_DOCS_QUICK_ACCESS['dev_token_setup']
first_api_call = GOOGLE_ADS_DOCS_QUICK_ACCESS['first_api_call']

# Iterate through specific category
for key, url in GOOGLE_ADS_DOCS_CATEGORIES['get_started'].items():
    print(f"{key}: {url}")

# Use in API responses or documentation
def get_help_urls():
    return {
        'getting_started': GOOGLE_ADS_DOCS_QUICK_ACCESS['getting_started'],
        'oauth_setup': GOOGLE_ADS_DOCS_QUICK_ACCESS['oauth_setup'],
        'common_errors': GOOGLE_ADS_DOCS_QUICK_ACCESS['common_errors']
    }
""")

if __name__ == "__main__":
    test_constants()
    show_usage_examples()
    
    print("\n" + "=" * 60)
    print("Test completed!")
