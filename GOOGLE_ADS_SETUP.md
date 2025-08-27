# 🔑 Google Ads API Setup Guide

This guide will walk you through setting up Google Ads API credentials for the Marketing Assistant chat feature.

## 📋 Prerequisites

- Google Ads account with admin access
- Google Cloud Project
- Basic understanding of OAuth 2.0

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create New Project** or select existing one
3. **Enable Required APIs**:
   - Google Ads API
   - Google OAuth2 API

### Step 2: Create OAuth 2.0 Credentials

1. **In Google Cloud Console**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/google-ads/oauth/callback/` (development)
     - `https://yourdomain.com/google-ads/oauth/callback/` (production)

2. **Download the credentials** (JSON file)
3. **Rename to**: `google_ads_credentials.json`
4. **Place in project root directory**

### Step 3: Get Google Ads Developer Token

1. **Go to Google Ads**: https://ads.google.com/
2. **Tools & Settings** → **Setup** → **API Center**
3. **Apply for developer token** (may take 1-2 business days)
4. **Copy the developer token**

### Step 4: Get Customer ID

1. **In Google Ads**: Look at the top right corner
2. **Customer ID** format: `123-456-7890`
3. **Copy this number**

### Step 5: Generate Refresh Token

1. **Install required packages**:
   ```bash
   pip install google-auth-oauthlib google-auth
   ```

2. **Run the token generator**:
   ```bash
   python generate_google_ads_token.py
   ```

3. **Follow the OAuth flow** in your browser
4. **Copy the refresh token** from the output

### Step 6: Update Environment Variables

Add these to your `.env` file:

```env
# Google Ads API Credentials
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_CUSTOMER_ID=

# Optional: Login Customer ID (for MCC accounts)
GOOGLE_ADS_LOGIN_CUSTOMER_ID=

## 🔧 Troubleshooting

### Common Issues

1. **"invalid_grant" Error**:
   - Refresh token may have expired
   - Re-run the token generator
   - Check OAuth consent screen settings

2. **"Access Denied" Error**:
   - Ensure Google Ads API is enabled
   - Check account permissions
   - Verify customer ID is correct

3. **"Developer Token Not Approved"**:
   - Wait for developer token approval (1-2 business days)
   - Check application status in Google Ads

### OAuth Consent Screen

1. **In Google Cloud Console**:
   - Go to "APIs & Services" → "OAuth consent screen"
   - Add your email as a test user
   - Publish the app (if needed)

## 📱 Testing the Setup

1. **Restart Django server** after updating `.env`
2. **Visit chat dashboard**: http://localhost:8000/google-ads/chat/
3. **Try asking**: "Show me my campaign performance"
4. **Expected result**: Real Google Ads data instead of error messages

## 🔒 Security Notes

- **Never commit** `.env` file to version control
- **Keep credentials secure** and rotate regularly
- **Use environment variables** in production
- **Monitor API usage** to avoid quotas

## 📚 Additional Resources

- [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
- [OAuth 2.0 Setup Guide](https://developers.google.com/google-ads/api/docs/oauth/overview)
- [Google Cloud Console](https://console.cloud.google.com/)

## 🆘 Need Help?

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all credentials are correct
3. Ensure APIs are enabled
4. Check Google Ads account permissions
5. Review Django server logs for specific error messages

---

**Note**: The first-time setup may take 15-30 minutes, but subsequent uses will be much faster!
