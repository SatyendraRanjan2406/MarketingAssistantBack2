#!/bin/bash
# Script to load environment variables from .env file

echo "Loading environment variables from .env file..."

# Load environment variables
set -a
source .env
set +a

echo "✅ Environment variables loaded successfully!"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:0:20}..." # Show first 20 chars for security
echo "Django SECRET_KEY: ${SECRET_KEY:0:20}..." # Show first 20 chars for security

# Check if required variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY is not set!"
    exit 1
else
    echo "✅ OPENAI_API_KEY is set"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY is not set!"
    exit 1
else
    echo "✅ SECRET_KEY is set"
fi

echo "🎉 All environment variables loaded successfully!"
