# Security Setup Guide

## ⚠️ IMPORTANT: Never commit sensitive files to Git!

This repository contains sensitive configuration files that should **NEVER** be committed to version control.

## 🚨 CRITICAL SECRETS FOUND IN CODE

### **1. Django Secret Key (HIGH PRIORITY)**
- **File:** `marketing_assistant_project/settings.py:27`
- **Current:** Hardcoded in settings file
- **Action:** Move to `DJANGO_SECRET_KEY` environment variable

### **2. Database Credentials (HIGH PRIORITY)**
- **File:** `marketing_assistant_project/settings.py:75-80`
- **Current:** Default values exposed in code
- **Action:** Move to environment variables: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

### **3. Google OAuth Credentials (HIGH PRIORITY)**
- **Files:** Multiple files reference these
- **Required:** `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REDIRECT_URI`
- **Action:** Move to environment variables

### **4. Google Ads API Credentials (HIGH PRIORITY)**
- **Files:** Multiple files reference these
- **Required:** `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`
- **Action:** Move to environment variables

### **5. OpenAI API Key (HIGH PRIORITY)**
- **Files:** Multiple files reference this
- **Required:** `OPENAI_API_KEY`
- **Action:** Move to environment variable

### **6. JWT Configuration (MEDIUM PRIORITY)**
- **File:** `marketing_assistant_project/settings.py:185`
- **Current:** Uses Django SECRET_KEY
- **Action:** Consider separate JWT secret key

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
# Copy the complete template file
cp .env.complete.template .env

# Edit with your actual values
nano .env
```

### 2. Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API and Google Ads API
4. Create OAuth 2.0 credentials
5. Add the credentials to your `.env` file

### 3. Google Ads Setup
1. Get your Google Ads Developer Token
2. Download your Google Ads API credentials
3. Generate a refresh token using the provided scripts
4. Add all credentials to your `.env` file

### 4. OpenAI Setup
1. Get your API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to `.env` file as `OPENAI_API_KEY`

### 5. Database Setup
1. Create your PostgreSQL database
2. Update database credentials in `.env` file

### 6. Django Secret Key
1. Generate a new secret key:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```
2. Add to `.env` file as `DJANGO_SECRET_KEY`

## Security Checklist

- [ ] Django SECRET_KEY moved to environment variable
- [ ] Database credentials moved to environment variables
- [ ] Google OAuth credentials moved to environment variables
- [ ] Google Ads API credentials moved to environment variables
- [ ] OpenAI API key moved to environment variable
- [ ] All `.env*` files added to `.gitignore`
- [ ] All credential JSON files added to `.gitignore`
- [ ] No hardcoded secrets remain in code
- [ ] Environment template files created
- [ ] Security documentation updated

## Emergency Actions

If you accidentally committed secrets:
1. **IMMEDIATELY** revoke/rotate all exposed credentials
2. Use `git filter-branch` or BFG to remove from history
3. Force push to overwrite remote repository
4. Notify your team and security team
5. Review all recent commits for other secrets
