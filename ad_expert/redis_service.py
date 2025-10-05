"""
Redis Service for managing customer IDs and conversation data
"""

import json
import logging
from typing import Optional, List, Dict, Any
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Service for managing data in Redis cache"""
    
    # Key prefixes for different data types
    CUSTOMER_ID_PREFIX = "customer_id"
    CONVERSATION_PREFIX = "conversation"
    USER_SESSION_PREFIX = "user_session"
    
    @classmethod
    def _get_customer_key(cls, user_id: int, conversation_id: int) -> str:
        """Generate Redis key for customer ID"""
        return f"{cls.CUSTOMER_ID_PREFIX}:user_{user_id}:conv_{conversation_id}"
    
    @classmethod
    def _get_conversation_key(cls, conversation_id: int) -> str:
        """Generate Redis key for conversation data"""
        return f"{cls.CONVERSATION_PREFIX}:{conversation_id}"
    
    @classmethod
    def _get_user_session_key(cls, user_id: int) -> str:
        """Generate Redis key for user session data"""
        return f"{cls.USER_SESSION_PREFIX}:{user_id}"
    
    @classmethod
    def save_customer_id(cls, user_id: int, conversation_id: int, customer_id: str, 
                        accessible_customers: List[str] = None) -> bool:
        """
        Save customer ID selection to Redis
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            customer_id: Selected customer ID
            accessible_customers: List of accessible customer IDs
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            key = cls._get_customer_key(user_id, conversation_id)
            
            # Prepare data to store
            data = {
                'customer_id': customer_id,
                'accessible_customers': accessible_customers or [],
                'selected_at': cache.get('current_timestamp', 'unknown')
            }
            
            # Save with 24 hour expiration
            cache.set(key, json.dumps(data), timeout=86400)
            
            logger.info(f"Saved customer ID {customer_id} for user {user_id}, conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving customer ID to Redis: {e}")
            return False
    
    @classmethod
    def get_customer_id(cls, user_id: int, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get customer ID selection from Redis
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            
        Returns:
            Dict with customer data or None if not found
        """
        try:
            key = cls._get_customer_key(user_id, conversation_id)
            data = cache.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting customer ID from Redis: {e}")
            return None
    
    @classmethod
    def save_accessible_customers(cls, user_id: int, accessible_customers: List[str]) -> bool:
        """
        Save accessible customers list for a user
        
        Args:
            user_id: User ID
            accessible_customers: List of accessible customer IDs
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            key = f"{cls.USER_SESSION_PREFIX}:{user_id}:accessible_customers"
            
            data = {
                'accessible_customers': accessible_customers,
                'updated_at': cache.get('current_timestamp', 'unknown')
            }
            
            # Save with 1 hour expiration
            cache.set(key, json.dumps(data), timeout=3600)
            
            logger.info(f"Saved {len(accessible_customers)} accessible customers for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving accessible customers to Redis: {e}")
            return False
    
    @classmethod
    def get_accessible_customers(cls, user_id: int) -> Optional[List[str]]:
        """
        Get accessible customers list for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of accessible customer IDs or None if not found
        """
        try:
            key = f"{cls.USER_SESSION_PREFIX}:{user_id}:accessible_customers"
            data = cache.get(key)
            
            if data:
                parsed_data = json.loads(data)
                return parsed_data.get('accessible_customers', [])
            return None
            
        except Exception as e:
            logger.error(f"Error getting accessible customers from Redis: {e}")
            return None
    
    @classmethod
    def save_conversation_context(cls, conversation_id: int, context_data: Dict[str, Any]) -> bool:
        """
        Save conversation context data to Redis
        
        Args:
            conversation_id: Conversation ID
            context_data: Context data to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            key = cls._get_conversation_key(conversation_id)
            
            data = {
                'context': context_data,
                'updated_at': cache.get('current_timestamp', 'unknown')
            }
            
            # Save with 1 hour expiration
            cache.set(key, json.dumps(data), timeout=3600)
            
            logger.info(f"Saved conversation context for conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation context to Redis: {e}")
            return False
    
    @classmethod
    def get_conversation_context(cls, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get conversation context data from Redis
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict with context data or None if not found
        """
        try:
            key = cls._get_conversation_key(conversation_id)
            data = cache.get(key)
            
            if data:
                parsed_data = json.loads(data)
                return parsed_data.get('context', {})
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation context from Redis: {e}")
            return None
    
    @classmethod
    def delete_customer_selection(cls, user_id: int, conversation_id: int) -> bool:
        """
        Delete customer ID selection from Redis
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            key = cls._get_customer_key(user_id, conversation_id)
            cache.delete(key)
            
            logger.info(f"Deleted customer selection for user {user_id}, conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting customer selection from Redis: {e}")
            return False
    
    @classmethod
    def clear_user_data(cls, user_id: int) -> bool:
        """
        Clear all Redis data for a user
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        try:
            # Get all keys for this user
            pattern = f"{cls.USER_SESSION_PREFIX}:{user_id}:*"
            keys = cache.keys(pattern)
            
            # Also get customer ID keys for this user
            customer_pattern = f"{cls.CUSTOMER_ID_PREFIX}:user_{user_id}:*"
            customer_keys = cache.keys(customer_pattern)
            
            all_keys = keys + customer_keys
            
            if all_keys:
                cache.delete_many(all_keys)
                logger.info(f"Cleared {len(all_keys)} Redis keys for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing user data from Redis: {e}")
            return False
    
    @classmethod
    def test_connection(cls) -> bool:
        """
        Test Redis connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            cache.set('test_key', 'test_value', timeout=10)
            result = cache.get('test_key')
            cache.delete('test_key')
            
            return result == 'test_value'
            
        except Exception as e:
            logger.error(f"Redis connection test failed: {e}")
            return False
