#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

print("Testing imports...")

try:
    from google.ads.googleads.client import GoogleAdsClient
    print("✅ GoogleAdsClient imported")
except Exception as e:
    print(f"❌ GoogleAdsClient import failed: {e}")

try:
    from google.ads.googleads.v21.services.types import SearchGoogleAdsStreamResponse, GoogleAdsRow
    print("✅ SearchGoogleAdsStreamResponse and GoogleAdsRow imported")
except Exception as e:
    print(f"❌ v21 types import failed: {e}")

try:
    from google.ads.googleads.v21.services import GoogleAdsServiceClient
    print("✅ GoogleAdsServiceClient imported")
except Exception as e:
    print(f"❌ GoogleAdsServiceClient import failed: {e}")

try:
    from google_ads_new.google_ads_api_service import GoogleAdsAPIService
    print("✅ GoogleAdsAPIService imported")
except Exception as e:
    print(f"❌ GoogleAdsAPIService import failed: {e}")

print("Import test completed!")
