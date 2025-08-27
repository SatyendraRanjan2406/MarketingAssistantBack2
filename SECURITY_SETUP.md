# Security Setup Guide

## ⚠️ IMPORTANT: Never commit sensitive files to Git!

This repository contains sensitive configuration files that should **NEVER** be committed to version control.

## Files to Keep Local Only

### Environment Variables
- `.env` - Contains API keys and secrets
- `.env.backup*` - Backup files with sensitive data
- Any file starting with `.env.`

### API Credentials
- `google_ads_credentials*.json` - Google Ads API credentials
- `google_ads_token*.json` - Google Ads access tokens
- Any file containing `credentials`, `token`, `secret`, or `key` in the name

## Setup Instructions

### 1. Copy Template Files
```bash
# Copy the template file
cp .env.template .env

# Edit with your actual values
nano .env
```

### 2. Google Ads Setup
1. Download your Google Ads API credentials from Google Cloud Console
2. Save as `google_ads_credentials.json` (local only)
3. Run the authentication flow to generate `google_ads_token.json` (local only)

### 3. OpenAI Setup
1. Get your API key from OpenAI
2. Add it to your `.env` file

## Security Best Practices

1. **Never commit `.env` files**
2. **Never commit API credentials or tokens**
3. **Use environment variables for all secrets**
4. **Regularly rotate API keys**
5. **Use different credentials for development/staging/production**

## If You Accidentally Commit Secrets

1. **Immediately revoke the exposed credentials**
2. **Remove files from Git history**
3. **Generate new credentials**
4. **Update all systems using the old credentials**

## File Structure
```
marketing_assistant/
├── .env.template          # Template for environment variables
├── .env                   # Your actual environment file (local only)
├── google_ads_credentials.json  # Google Ads credentials (local only)
├── google_ads_token.json        # Google Ads tokens (local only)
└── SECURITY_SETUP.md     # This file
```

## Need Help?
If you suspect credentials have been compromised:
1. Check your Git history
2. Revoke exposed credentials immediately
3. Generate new credentials
4. Update your local `.env` file
