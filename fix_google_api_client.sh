#!/bin/bash
# Fix Google API client missing modules

echo "🔧 Fixing Google API client issues..."
echo "====================================="

# 1. Install Google API client library
echo "📦 Installing Google API client library..."
pip install google-api-python-client

# 2. Install Google Auth libraries
echo "🔐 Installing Google Auth libraries..."
pip install google-auth google-auth-oauthlib google-auth-httplib2

# 3. Install Google Ads API
echo "📊 Installing Google Ads API..."
pip install google-ads

# 4. Install missing dependencies
echo "📦 Installing missing dependencies..."
pip install google-api-core google-api-python-client google-auth-oauthlib

# 5. Verify installation
echo "✅ Verifying Google API installation..."
python -c "from googleapiclient.discovery import build; print('Google API client is available')"

# 6. Test Django
echo "🧪 Testing Django..."
python manage.py check

echo "✅ Fix completed!"
