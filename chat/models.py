from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_other_participant(self, user):
        """Get the other participant in a two-person conversation"""
        return self.participants.exclude(id=user.id).first()
    
    def get_last_message(self):
        """Get the last message in the conversation"""
        return self.messages.order_by('-created_at').first()
    
    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}..."
    
    def mark_as_read(self):
        """Mark message as read if it's not already"""
        if not self.is_read:
            self.is_read = True
            self.save()
