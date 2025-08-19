# 🔑 Fixing OpenAI API Quota Exceeded Error

## ❌ The Problem
You're getting this error because your OpenAI API key has exceeded its quota:
```
Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details...'}}
```

## ✅ The Solution
I've updated your code to use environment variables instead of hardcoded API keys. Here's how to fix it:

### Step 1: Get a New OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in to your account
3. Check your billing and quota status
4. If needed, upgrade your plan or wait for quota reset
5. Create a new API key

### Step 2: Set Up Environment Variables
You have several options:

#### Option A: Use the Setup Script (Recommended)
```bash
python setup_env.py
```
This will guide you through setting up your `.env` file interactively.

#### Option B: Manual Setup
1. Edit the `.env` file in your project root
2. Replace `your_openai_api_key_here` with your actual API key:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

#### Option C: Export Environment Variable
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

### Step 3: Restart Your Django Server
After setting the environment variable, restart your Django server:
```bash
python manage.py runserver
```

## 🔍 What I Fixed

1. **Removed hardcoded API keys** from:
   - `google_ads_app/chat_service.py` (line 46)
   - `google_ads_app/views.py` (line 700)

2. **Updated code to use environment variables**:
   - The chat service now reads from `OPENAI_API_KEY` environment variable
   - Falls back gracefully when no API key is provided

3. **Created helpful files**:
   - `.env` - Your environment variables file
   - `.gitignore` - Prevents committing sensitive data
   - `setup_env.py` - Interactive setup script
   - `env_template.txt` - Template for manual setup

## 🚨 Security Notes

- **Never commit API keys** to version control
- The `.env` file is now in `.gitignore` to prevent accidental commits
- API keys are loaded from environment variables at runtime

## 🧪 Testing the Fix

1. Set your new API key in the `.env` file
2. Restart Django server
3. Try using the chat feature again
4. Check the console logs for successful API key loading

## 📞 If You Still Have Issues

1. **Check your OpenAI account billing** at [OpenAI Billing](https://platform.openai.com/account/billing)
2. **Verify your API key** is correct and active
3. **Check your quota limits** and usage
4. **Ensure the `.env` file** is in your project root directory
5. **Restart Django** after making changes

## 💡 Alternative Solutions

If you continue to have quota issues:

1. **Upgrade your OpenAI plan** for higher limits
2. **Use a different OpenAI account** with available quota
3. **Implement rate limiting** in your application
4. **Add fallback responses** when API is unavailable

## 🔄 Code Changes Made

The main changes were in these files:

```python
# Before (HARDCODED - REMOVED):
self.openai_api_key = "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"

# After (ENVIRONMENT VARIABLE):
self.openai_api_key = os.getenv('OPENAI_API_KEY')
```

Your application will now work securely with environment variables! 🎉
