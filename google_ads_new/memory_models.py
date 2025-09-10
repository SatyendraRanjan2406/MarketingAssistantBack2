from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class UserMemory(models.Model):
    """Long-term user memory and preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='memory')
    preferences = models.JSONField(default=dict, help_text="User preferences and settings")
    learning_patterns = models.JSONField(default=dict, help_text="Learned user behavior patterns")
    expertise_level = models.CharField(
        max_length=20, 
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert')
        ],
        default='beginner'
    )
    favorite_topics = models.JSONField(default=list, help_text="Topics user frequently asks about")
    preferred_analysis_depth = models.IntegerField(default=1, help_text="Preferred dig deeper depth")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_memory'
        verbose_name = 'User Memory'
        verbose_name_plural = 'User Memories'

    def update_preferences(self, new_preferences: Dict[str, Any]):
        """Update user preferences"""
        current = self.preferences or {}
        current.update(new_preferences)
        self.preferences = current
        self.save()

    def learn_pattern(self, pattern_type: str, data: Dict[str, Any]):
        """Learn from user behavior patterns"""
        if pattern_type not in self.learning_patterns:
            self.learning_patterns[pattern_type] = []
        
        self.learning_patterns[pattern_type].append({
            'data': data,
            'timestamp': timezone.now().isoformat(),
            'confidence': data.get('confidence', 0.5)
        })
        self.save()

    def get_adaptive_response(self, query_type: str) -> Dict[str, Any]:
        """Get adaptive response based on learned patterns"""
        if query_type in self.learning_patterns:
            patterns = self.learning_patterns[query_type]
            if patterns:
                # Get most recent and confident pattern
                latest_pattern = max(patterns, key=lambda x: x['confidence'])
                return latest_pattern['data']
        return {}


class ConversationMemory(models.Model):
    """Persistent conversation history and context"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    session_id = models.CharField(max_length=255, unique=True)
    google_ads_account = models.CharField(max_length=255, null=True, blank=True)
    conversation_history = models.JSONField(default=list, help_text="Full conversation history")
    context_summary = models.JSONField(default=dict, help_text="Context summary for memory")
    intent_history = models.JSONField(default=list, help_text="Intent classification history")
    analysis_results = models.JSONField(default=list, help_text="Analysis results and insights")
    creative_generations = models.JSONField(default=list, help_text="Generated creative content")
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'conversation_memory'
        verbose_name = 'Conversation Memory'
        verbose_name_plural = 'Conversation Memories'
        indexes = [
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['last_activity']),
        ]

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation history"""
        message = {
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': timezone.now().isoformat(),
            'metadata': metadata or {}
        }
        self.conversation_history.append(message)
        self.last_activity = timezone.now()
        self.save()

    def add_intent(self, intent: Dict[str, Any]):
        """Add intent classification to history"""
        intent_record = {
            'intent': intent,
            'timestamp': timezone.now().isoformat()
        }
        self.intent_history.append(intent_record)
        self.save()

    def add_analysis_result(self, analysis: Dict[str, Any]):
        """Add analysis result to memory"""
        analysis_record = {
            'analysis': analysis,
            'timestamp': timezone.now().isoformat()
        }
        self.analysis_results.append(analysis_record)
        self.save()

    def add_creative_generation(self, creative: Dict[str, Any]):
        """Add creative generation to memory"""
        creative_record = {
            'creative': creative,
            'timestamp': timezone.now().isoformat()
        }
        self.creative_generations.append(creative_record)
        self.save()

    def get_context_summary(self) -> Dict[str, Any]:
        """Get context summary for memory"""
        if not self.context_summary:
            # Generate context summary from conversation
            summary = {
                'topics_discussed': self._extract_topics(),
                'user_preferences': self._extract_preferences(),
                'analysis_focus': self._extract_analysis_focus(),
                'creative_style': self._extract_creative_style()
            }
            self.context_summary = summary
            self.save()
        
        return self.context_summary

    def _extract_topics(self) -> List[str]:
        """Extract main topics from conversation"""
        topics = set()
        for message in self.conversation_history:
            if message['role'] == 'user':
                content = message['content'].lower()
                if 'campaign' in content:
                    topics.add('campaign_management')
                if 'performance' in content:
                    topics.add('performance_analysis')
                if 'creative' in content or 'ad copy' in content:
                    topics.add('creative_generation')
                if 'optimization' in content:
                    topics.add('optimization')
        return list(topics)

    def _extract_preferences(self) -> Dict[str, Any]:
        """Extract user preferences from conversation"""
        preferences = {}
        for message in self.conversation_history:
            if message['role'] == 'user':
                content = message['content'].lower()
                if 'detailed' in content or 'deep' in content:
                    preferences['analysis_depth'] = 'detailed'
                if 'simple' in content or 'summary' in content:
                    preferences['analysis_depth'] = 'simple'
                if 'visual' in content or 'chart' in content:
                    preferences['preferred_format'] = 'visual'
                if 'table' in content or 'data' in content:
                    preferences['preferred_format'] = 'tabular'
        return preferences

    def _extract_analysis_focus(self) -> Dict[str, Any]:
        """Extract analysis focus areas"""
        focus = {}
        for result in self.analysis_results:
            analysis = result.get('analysis', {})
            if 'campaign' in analysis:
                focus['campaign_analysis'] = True
            if 'performance' in analysis:
                focus['performance_analysis'] = True
            if 'trends' in analysis:
                focus['trend_analysis'] = True
        return focus

    def _extract_creative_style(self) -> Dict[str, Any]:
        """Extract creative style preferences"""
        style = {}
        for creative in self.creative_generations:
            creative_data = creative.get('creative', {})
            if 'color_scheme' in creative_data:
                style['preferred_colors'] = creative_data['color_scheme']
            if 'template_type' in creative_data:
                style['preferred_templates'] = creative_data['template_type']
        return style

    def get_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        return self.conversation_history[-limit:]

    def get_similar_conversations(self, user_id: int, limit: int = 3) -> List['ConversationMemory']:
        """Get similar conversations from user's history"""
        from django.db.models import Q
        
        # Find conversations with similar topics
        user_conversations = ConversationMemory.objects.filter(
            user_id=user_id,
            is_active=False
        ).exclude(id=self.id)
        
        # Simple similarity based on topics
        current_topics = set(self._extract_topics())
        similar_conversations = []
        
        for conv in user_conversations:
            conv_topics = set(conv._extract_topics())
            similarity = len(current_topics.intersection(conv_topics))
            if similarity > 0:
                similar_conversations.append((conv, similarity))
        
        # Sort by similarity and return top matches
        similar_conversations.sort(key=lambda x: x[1], reverse=True)
        return [conv for conv, _ in similar_conversations[:limit]]


class CrossSessionMemory(models.Model):
    """Cross-session context sharing and learning"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cross_session_memory')
    memory_type = models.CharField(max_length=50, help_text="Type of cross-session memory")
    memory_key = models.CharField(max_length=255, help_text="Key identifier for the memory")
    memory_data = models.JSONField(default=dict, help_text="Memory data and context")
    importance_score = models.FloatField(default=0.5, help_text="Importance of this memory")
    access_count = models.IntegerField(default=0, help_text="Number of times accessed")
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Memory expiration date")

    class Meta:
        db_table = 'cross_session_memory'
        verbose_name = 'Cross Session Memory'
        verbose_name_plural = 'Cross Session Memories'
        unique_together = ['user', 'memory_type', 'memory_key']
        indexes = [
            models.Index(fields=['user', 'memory_type']),
            models.Index(fields=['importance_score']),
            models.Index(fields=['expires_at']),
        ]

    def access_memory(self):
        """Mark memory as accessed"""
        self.access_count += 1
        self.last_accessed = timezone.now()
        self.save()

    def update_importance(self, new_score: float):
        """Update memory importance score"""
        self.importance_score = max(0.0, min(1.0, new_score))
        self.save()

    def is_expired(self) -> bool:
        """Check if memory has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @classmethod
    def get_relevant_memories(cls, user_id: int, context: str, limit: int = 5) -> List['CrossSessionMemory']:
        """Get relevant cross-session memories for given context"""
        # Simple keyword-based relevance (could be enhanced with embeddings)
        relevant_memories = cls.objects.filter(
            user_id=user_id,
            expires_at__isnull=True
        ).filter(
            models.Q(memory_data__icontains=context) |
            models.Q(memory_key__icontains=context)
        ).order_by('-importance_score', '-access_count')[:limit]
        
        return relevant_memories

    @classmethod
    def cleanup_expired_memories(cls):
        """Clean up expired memories"""
        expired = cls.objects.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        return count


class AdaptiveResponsePattern(models.Model):
    """Learned response patterns for user adaptation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='response_patterns')
    pattern_type = models.CharField(max_length=50, help_text="Type of response pattern")
    trigger_conditions = models.JSONField(default=dict, help_text="Conditions that trigger this pattern")
    response_template = models.JSONField(default=dict, help_text="Response template and structure")
    success_rate = models.FloatField(default=0.0, help_text="Success rate of this pattern")
    usage_count = models.IntegerField(default=0, help_text="Number of times used")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'adaptive_response_patterns'
        verbose_name = 'Adaptive Response Pattern'
        verbose_name_plural = 'Adaptive Response Patterns'
        unique_together = ['user', 'pattern_type']

    def update_success_rate(self, was_successful: bool):
        """Update pattern success rate"""
        total_usage = self.usage_count + 1
        current_success = self.success_rate * self.usage_count
        
        if was_successful:
            new_success = current_success + 1
        else:
            new_success = current_success
        
        self.success_rate = new_success / total_usage
        self.usage_count = total_usage
        self.save()

    def should_use_pattern(self, context: Dict[str, Any]) -> bool:
        """Determine if pattern should be used for given context"""
        # Check if trigger conditions match
        for key, value in self.trigger_conditions.items():
            if key not in context or context[key] != value:
                return False
        
        # Check success rate threshold
        return self.success_rate > 0.6 and self.usage_count > 3

    @classmethod
    def get_best_pattern(cls, user_id: int, pattern_type: str, context: Dict[str, Any]) -> Optional['AdaptiveResponsePattern']:
        """Get the best response pattern for given context"""
        patterns = cls.objects.filter(
            user_id=user_id,
            pattern_type=pattern_type
        )
        
        best_pattern = None
        best_score = 0.0
        
        for pattern in patterns:
            if pattern.should_use_pattern(context):
                # Score based on success rate and usage count
                score = pattern.success_rate * (1 + pattern.usage_count * 0.1)
                if score > best_score:
                    best_score = score
                    best_pattern = pattern
        
        return best_pattern
