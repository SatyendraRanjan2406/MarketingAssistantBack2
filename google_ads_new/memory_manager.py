from typing import Dict, List, Any, Optional, Tuple
from django.contrib.auth.models import User
from django.utils import timezone
from .memory_models import (
    UserMemory, ConversationMemory, CrossSessionMemory, 
    AdaptiveResponsePattern
)
import json
import logging

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages all memory operations for the AI chatbot"""
    
    def __init__(self, user: User):
        self.user = user
        self.user_memory = self._get_or_create_user_memory()
    
    def _get_or_create_user_memory(self) -> UserMemory:
        """Get or create user memory"""
        user_memory, created = UserMemory.objects.get_or_create(user=self.user)
        if created:
            logger.info(f"Created new user memory for user {self.user.id}")
        return user_memory
    
    # ==================== CONVERSATION MEMORY ====================
    
    def create_conversation_session(self, session_id: str, google_ads_account: str = None) -> ConversationMemory:
        """Create a new conversation session"""
        conversation = ConversationMemory.objects.create(
            user=self.user,
            session_id=session_id,
            google_ads_account=google_ads_account,
            is_active=True
        )
        logger.info(f"Created conversation session {session_id} for user {self.user.id}")
        return conversation
    
    def get_conversation_session(self, session_id: str) -> Optional[ConversationMemory]:
        """Get existing conversation session"""
        try:
            return ConversationMemory.objects.get(
                user=self.user,
                session_id=session_id,
                is_active=True
            )
        except ConversationMemory.DoesNotExist:
            return None
    
    def add_user_message(self, session_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add user message to conversation history"""
        conversation = self.get_conversation_session(session_id)
        if conversation:
            conversation.add_message('user', content, metadata)
            self._learn_from_user_message(content, metadata)
    
    def add_assistant_message(self, session_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add assistant message to conversation history"""
        conversation = self.get_conversation_session(session_id)
        if conversation:
            conversation.add_message('assistant', content, metadata)
    
    def add_intent(self, session_id: str, intent: Dict[str, Any]):
        """Add intent classification to conversation"""
        conversation = self.get_conversation_session(session_id)
        if conversation:
            conversation.add_intent(intent)
            self._learn_from_intent(intent)
    
    def add_analysis_result(self, session_id: str, analysis: Dict[str, Any]):
        """Add analysis result to conversation"""
        conversation = self.get_conversation_session(session_id)
        if conversation:
            conversation.add_analysis_result(analysis)
    
    def add_creative_generation(self, session_id: str, creative: Dict[str, Any]):
        """Add creative generation to conversation"""
        conversation = self.get_conversation_session(session_id)
        if conversation:
            conversation.add_creative_generation(creative)
            self._learn_from_creative_generation(creative)
    
    def end_conversation_session(self, session_id: str):
        """End a conversation session"""
        conversation = self.get_conversation_session(session_id)
        if conversation:
            conversation.is_active = False
            conversation.save()
            
            # Generate and store context summary
            context_summary = conversation.get_context_summary()
            
            # Store important insights in cross-session memory
            self._store_cross_session_insights(context_summary)
            
            logger.info(f"Ended conversation session {session_id} for user {self.user.id}")
    
    # ==================== USER PREFERENCES & LEARNING ====================
    
    def update_user_preferences(self, new_preferences: Dict[str, Any]):
        """Update user preferences"""
        self.user_memory.update_preferences(new_preferences)
        logger.info(f"Updated preferences for user {self.user.id}")
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        return self.user_memory.preferences or {}
    
    def learn_user_pattern(self, pattern_type: str, data: Dict[str, Any]):
        """Learn from user behavior patterns"""
        self.user_memory.learn_pattern(pattern_type, data)
        logger.info(f"Learned pattern {pattern_type} for user {self.user.id}")
    
    def get_adaptive_response(self, query_type: str) -> Dict[str, Any]:
        """Get adaptive response based on learned patterns"""
        return self.user_memory.get_adaptive_response(query_type)
    
    def update_expertise_level(self, new_level: str):
        """Update user expertise level"""
        if new_level in ['beginner', 'intermediate', 'advanced', 'expert']:
            self.user_memory.expertise_level = new_level
            self.user_memory.save()
            logger.info(f"Updated expertise level to {new_level} for user {self.user.id}")
    
    def get_expertise_level(self) -> str:
        """Get user expertise level"""
        return self.user_memory.expertise_level
    
    # ==================== CROSS-SESSION MEMORY ====================
    
    def store_cross_session_memory(self, memory_type: str, memory_key: str, 
                                 memory_data: Dict[str, Any], importance_score: float = 0.5,
                                 expires_at: Optional[timezone.datetime] = None):
        """Store cross-session memory"""
        memory, created = CrossSessionMemory.objects.get_or_create(
            user=self.user,
            memory_type=memory_type,
            memory_key=memory_key,
            defaults={
                'memory_data': memory_data,
                'importance_score': importance_score,
                'expires_at': expires_at
            }
        )
        
        if not created:
            # Update existing memory
            memory.memory_data.update(memory_data)
            memory.importance_score = importance_score
            if expires_at:
                memory.expires_at = expires_at
            memory.save()
        
        logger.info(f"Stored cross-session memory {memory_type}:{memory_key} for user {self.user.id}")
    
    def get_relevant_cross_session_memories(self, context: str, limit: int = 5) -> List[CrossSessionMemory]:
        """Get relevant cross-session memories for given context"""
        return CrossSessionMemory.get_relevant_memories(self.user.id, context, limit)
    
    def access_cross_session_memory(self, memory_id: int):
        """Mark cross-session memory as accessed"""
        try:
            memory = CrossSessionMemory.objects.get(id=memory_id, user=self.user)
            memory.access_memory()
        except CrossSessionMemory.DoesNotExist:
            pass
    
    # ==================== ADAPTIVE RESPONSE PATTERNS ====================
    
    def store_response_pattern(self, pattern_type: str, trigger_conditions: Dict[str, Any],
                             response_template: Dict[str, Any]):
        """Store a new response pattern"""
        pattern, created = AdaptiveResponsePattern.objects.get_or_create(
            user=self.user,
            pattern_type=pattern_type,
            defaults={
                'trigger_conditions': trigger_conditions,
                'response_template': response_template,
                'success_rate': 0.0,
                'usage_count': 0
            }
        )
        
        if not created:
            # Update existing pattern
            pattern.trigger_conditions.update(trigger_conditions)
            pattern.response_template.update(response_template)
            pattern.save()
        
        logger.info(f"Stored response pattern {pattern_type} for user {self.user.id}")
    
    def get_best_response_pattern(self, pattern_type: str, context: Dict[str, Any]) -> Optional[AdaptiveResponsePattern]:
        """Get the best response pattern for given context"""
        return AdaptiveResponsePattern.get_best_pattern(self.user.id, pattern_type, context)
    
    def update_pattern_success(self, pattern_id: int, was_successful: bool):
        """Update pattern success rate"""
        try:
            pattern = AdaptiveResponsePattern.objects.get(id=pattern_id, user=self.user)
            pattern.update_success_rate(was_successful)
        except AdaptiveResponsePattern.DoesNotExist:
            pass
    
    # ==================== CONTEXT & INSIGHTS ====================
    
    def get_conversation_context(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        conversation = self.get_conversation_session(session_id)
        if conversation:
            return conversation.get_recent_context(limit)
        return []
    
    def get_similar_conversations(self, session_id: str, limit: int = 3) -> List[ConversationMemory]:
        """Get similar conversations from user's history"""
        conversation = self.get_conversation_session(session_id)
        if conversation:
            return conversation.get_similar_conversations(self.user.id, limit)
        return []
    
    def get_user_insights(self) -> Dict[str, Any]:
        """Get comprehensive user insights"""
        insights = {
            'expertise_level': self.user_memory.expertise_level,
            'preferences': self.user_memory.preferences,
            'favorite_topics': self.user_memory.favorite_topics,
            'preferred_analysis_depth': self.user_memory.preferred_analysis_depth,
            'learning_patterns': self.user_memory.learning_patterns,
            'total_conversations': ConversationMemory.objects.filter(user=self.user).count(),
            'active_conversations': ConversationMemory.objects.filter(user=self.user, is_active=True).count(),
            'cross_session_memories': CrossSessionMemory.objects.filter(user=self.user).count(),
            'response_patterns': AdaptiveResponsePattern.objects.filter(user=self.user).count()
        }
        return insights
    
    # ==================== PRIVATE LEARNING METHODS ====================
    
    def _learn_from_user_message(self, content: str, metadata: Dict[str, Any] = None):
        """Learn from user message content"""
        content_lower = content.lower()
        
        # Learn topic preferences
        topics = []
        if 'campaign' in content_lower:
            topics.append('campaign_management')
        if 'performance' in content_lower:
            topics.append('performance_analysis')
        if 'creative' in content_lower or 'ad copy' in content_lower:
            topics.append('creative_generation')
        if 'optimization' in content_lower:
            topics.append('optimization')
        if 'trends' in content_lower:
            topics.append('trend_analysis')
        
        if topics:
            current_topics = set(self.user_memory.favorite_topics or [])
            current_topics.update(topics)
            self.user_memory.favorite_topics = list(current_topics)
            self.user_memory.save()
        
        # Learn analysis depth preference
        if 'detailed' in content_lower or 'deep' in content_lower:
            self.user_memory.preferred_analysis_depth = max(2, self.user_memory.preferred_analysis_depth)
            self.user_memory.save()
        elif 'simple' in content_lower or 'summary' in content_lower:
            self.user_memory.preferred_analysis_depth = min(1, self.user_memory.preferred_analysis_depth)
            self.user_memory.save()
    
    def _learn_from_intent(self, intent: Dict[str, Any]):
        """Learn from user intent patterns"""
        action = intent.get('action', '')
        confidence = intent.get('confidence', 0.0)
        
        if confidence > 0.8:  # High confidence intent
            self.learn_user_pattern('intent_preference', {
                'action': action,
                'confidence': confidence,
                'frequency': 1
            })
    
    def _learn_from_creative_generation(self, creative: Dict[str, Any]):
        """Learn from creative generation preferences"""
        template_type = creative.get('template_type', '')
        color_scheme = creative.get('color_scheme', '')
        
        if template_type and color_scheme:
            self.learn_user_pattern('creative_preference', {
                'template_type': template_type,
                'color_scheme': color_scheme,
                'timestamp': timezone.now().isoformat()
            })
    
    def _store_cross_session_insights(self, context_summary: Dict[str, Any]):
        """Store important insights in cross-session memory"""
        topics = context_summary.get('topics_discussed', [])
        preferences = context_summary.get('user_preferences', {})
        
        # Store topic expertise
        for topic in topics:
            self.store_cross_session_memory(
                'topic_expertise',
                topic,
                {'expertise_level': 'growing', 'last_discussed': timezone.now().isoformat()},
                importance_score=0.7
            )
        
        # Store user preferences
        if preferences:
            self.store_cross_session_memory(
                'user_preferences',
                'current_preferences',
                preferences,
                importance_score=0.8
            )
    
    # ==================== MEMORY CLEANUP ====================
    
    def cleanup_expired_memories(self) -> int:
        """Clean up expired cross-session memories"""
        return CrossSessionMemory.cleanup_expired_memories()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for the user"""
        return {
            'user_memory': {
                'expertise_level': self.user_memory.expertise_level,
                'preferences_count': len(self.user_memory.preferences or {}),
                'learning_patterns_count': len(self.user_memory.learning_patterns or {}),
                'favorite_topics_count': len(self.user_memory.favorite_topics or [])
            },
            'conversation_memory': {
                'total_conversations': ConversationMemory.objects.filter(user=self.user).count(),
                'active_conversations': ConversationMemory.objects.filter(user=self.user, is_active=True).count()
            },
            'cross_session_memory': {
                'total_memories': CrossSessionMemory.objects.filter(user=self.user).count(),
                'expired_memories': CrossSessionMemory.objects.filter(user=self.user, expires_at__lt=timezone.now()).count()
            },
            'adaptive_patterns': {
                'total_patterns': AdaptiveResponsePattern.objects.filter(user=self.user).count(),
                'high_success_patterns': AdaptiveResponsePattern.objects.filter(
                    user=self.user, success_rate__gt=0.8
                ).count()
            }
        }
