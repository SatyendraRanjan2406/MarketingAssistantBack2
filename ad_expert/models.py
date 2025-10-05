from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Conversation(models.Model):
    """Chat conversation - only stores natural language messages"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ad_expert_conversations')
    title = models.CharField(max_length=200, blank=True)
    customer_id = models.CharField(max_length=100, blank=True, null=True, help_text="Google Ads customer ID for this conversation")
    pending_query = models.TextField(blank=True, null=True, help_text="Query to execute after customer selection")
    pending_intent_result = models.JSONField(null=True, blank=True, help_text="Intent mapping result to execute after customer selection")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.user.username}"


class ChatMessage(models.Model):
    """Individual chat messages - only natural language content"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    response_type = models.CharField(max_length=20, default='text', blank=True)  # text, table, chart, etc.
    structured_data = models.JSONField(null=True, blank=True)  # For charts, tables, action items
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


# OAuth connections are now handled by the accounts app
# Google OAuth: Use UserGoogleAuth model from accounts app
# Meta OAuth: Can be added to accounts app if needed
