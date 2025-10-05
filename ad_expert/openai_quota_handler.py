"""
OpenAI Quota Handler
Handles quota exceeded errors with retry logic and fallbacks
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional
from openai import OpenAI, RateLimitError, APIConnectionError, APITimeoutError
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class OpenAIQuotaHandler:
    """Handles OpenAI API quota issues with retry logic and fallbacks"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.max_retries = 3
        self.base_delay = 1  # seconds
        self.max_delay = 60  # seconds
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        return delay + (time.time() % 1)  # Add jitter
    
    async def _make_request_with_retry(self, request_func, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Make OpenAI API request with retry logic"""
        if not self.client:
            return {"error": "OpenAI client not initialized"}
        
        for attempt in range(self.max_retries):
            try:
                result = await request_func(*args, **kwargs)
                return result
                
            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    logger.warning(f"Rate limit exceeded, retrying in {delay:.2f}s (attempt {attempt + 1}/{self.max_retries})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"Rate limit exceeded after {self.max_retries} attempts: {e}")
                    return {"error": "Rate limit exceeded", "retry_after": 60}
                    
            except (APIConnectionError, APITimeoutError) as e:
                if attempt < self.max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    logger.warning(f"API connection error, retrying in {delay:.2f}s (attempt {attempt + 1}/{self.max_retries})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"API connection failed after {self.max_retries} attempts: {e}")
                    return {"error": "API connection failed"}
                    
            except Exception as e:
                if "quota" in str(e).lower() or "insufficient_quota" in str(e).lower():
                    logger.error(f"Quota exceeded: {e}")
                    return {"error": "Quota exceeded", "message": str(e)}
                else:
                    logger.error(f"Unexpected error: {e}")
                    return {"error": str(e)}
        
        return {"error": "Max retries exceeded"}
    
    async def generate_chat_completion(self, messages: list, model: str = "gpt-3.5-turbo", **kwargs) -> Optional[Dict[str, Any]]:
        """Generate chat completion with retry logic"""
        async def _request():
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.dict() if response.usage else None,
                "model": response.model
            }
        
        return await self._make_request_with_retry(_request)
    
    async def generate_embeddings(self, input_text: str, model: str = "text-embedding-ada-002") -> Optional[Dict[str, Any]]:
        """Generate embeddings with retry logic"""
        async def _request():
            response = self.client.embeddings.create(
                model=model,
                input=input_text
            )
            return {
                "embeddings": response.data[0].embedding,
                "usage": response.usage.dict() if response.usage else None,
                "model": response.model
            }
        
        return await self._make_request_with_retry(_request)
    
    def get_fallback_response(self, query: str, error_type: str = "quota_exceeded") -> Dict[str, Any]:
        """Get fallback response when OpenAI is unavailable"""
        
        if error_type == "quota_exceeded":
            return {
                "content": f"""I apologize, but I'm currently experiencing high demand and have reached my API quota limit. Here's what I can help you with:

**🔧 Immediate Solutions:**
1. **Check your OpenAI billing** at https://platform.openai.com/account/billing
2. **Add payment method** or upgrade your plan
3. **Wait for quota reset** if you're on the free tier

**📊 For your query: "{query}"**
I can still help you with:
- Basic Google Ads data retrieval (without AI analysis)
- Account information and campaign data
- Performance metrics and reports
- Campaign management operations

**💡 Alternative Options:**
- Try again in a few minutes
- Use the basic data retrieval features
- Contact support if the issue persists

Would you like me to retrieve your Google Ads data without AI enhancement?""",
                "type": "quota_exceeded_fallback",
                "suggestions": [
                    "Show me my campaigns",
                    "Get account overview",
                    "Check performance data",
                    "List accessible customers"
                ]
            }
        
        elif error_type == "rate_limit":
            return {
                "content": f"""I'm experiencing high traffic right now. Please try again in a moment.

**For your query: "{query}"**
I'll process this as soon as the rate limit resets (usually within a minute).

**Quick alternatives:**
- Basic data retrieval (no AI analysis)
- Direct Google Ads API calls
- Account information lookup

Would you like to try a basic data request instead?""",
                "type": "rate_limit_fallback"
            }
        
        else:
            return {
                "content": f"""I encountered a technical issue while processing your request.

**For your query: "{query}"**
I can still help you with basic Google Ads operations:
- Campaign data retrieval
- Performance metrics
- Account information
- Campaign management

Would you like to try a different approach?""",
                "type": "general_fallback"
            }
    
    def is_quota_error(self, error_message: str) -> bool:
        """Check if error is quota-related"""
        quota_keywords = [
            "quota", "insufficient_quota", "billing", "payment", 
            "exceeded", "limit", "429"
        ]
        return any(keyword in error_message.lower() for keyword in quota_keywords)
    
    def get_retry_after_time(self, error_message: str) -> int:
        """Extract retry-after time from error message"""
        try:
            # Look for retry-after in error message
            if "retry" in error_message.lower():
                # Default to 60 seconds if not specified
                return 60
        except:
            pass
        return 60

# Global instance
quota_handler = OpenAIQuotaHandler()
