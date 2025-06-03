from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Base Post model with common fields
class BasePost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.FileField(upload_to='post_media', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='%(class)s_likes', blank=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def get_post_type(self):
        """Get the type of this post"""
        if isinstance(self, NormalPost):
            return 'normal'
        elif isinstance(self, AnnouncementPost):
            return 'announcement'
        elif isinstance(self, CommunityPost):
            return 'community'
        return 'unknown'
    
    def get_post_type_display(self):
        """Get the display name for the post type"""
        post_type = self.get_post_type()
        if post_type == 'normal':
            return 'Normal Post'
        elif post_type == 'announcement':
            return 'Announcement'
        elif post_type == 'community':
            return 'Community Post'
        return 'Unknown Post Type'
    
    def get_url_kwargs(self):
        """Get kwargs for URL patterns"""
        return {
            'pk': self.id,
            'post_type': self.get_post_type()
        }
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse(f'{self._meta.model_name}-detail', kwargs={'pk': self.pk})
    
    def get_like_count(self):
        return self.likes.count()
    
    def get_detail_url(self):
        return f'post-{self.get_post_type()}-detail'

    def get_update_url(self):
        return f'post-{self.get_post_type()}-update'

    def get_delete_url(self):
        return f'post-{self.get_post_type()}-delete'

    @property
    def image_url(self):
        try:
            if self.image and hasattr(self.image, 'url'):
                return self.image.url
        except Exception:
            pass
        return None
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Try to resize if it's an image file
        try:
            if self.image and hasattr(self.image, 'path'):
                file_name = self.image.name.lower()
                if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    img = Image.open(self.image.path)
                    if img.height > 800 or img.width > 800:
                        output_size = (800, 800)
                        img.thumbnail(output_size)
                        img.save(self.image.path)
        except Exception as e:
            print(f"Error processing post image: {e}")

    def get_post_type(self):
        """Get the type of this post"""
        if isinstance(self, NormalPost):
            return 'normal'
        elif isinstance(self, AnnouncementPost):
            return 'announcement'
        elif isinstance(self, CommunityPost):
            return 'community'
        return 'unknown'
    
    def get_post_type_display(self):
        """Get the display name for the post type"""
        post_type = self.get_post_type()
        if post_type == 'normal':
            return 'Normal Post'
        elif post_type == 'announcement':
            return 'Announcement'
        elif post_type == 'community':
            return 'Community Post'
        return 'Unknown Post Type'

    def get_url_kwargs(self):
        """Get kwargs for URL patterns"""
        return {
            'pk': self.id,
            'post_type': self.get_post_type()
        }

# Normal Post - Regular user posts
class NormalPost(BasePost):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_type = 'normal'

# Announcement Post - Special posts for announcements
class AnnouncementPost(BasePost):
    event_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_type = 'announcement'
    
    @property
    def is_past_event(self):
        return self.event_date < timezone.now()

# Community Post - Posts for community discussions
class CommunityPost(BasePost):
    is_sticky = models.BooleanField(default=False, help_text='If checked, this post will be pinned to the top.')
    category = models.CharField(max_length=50, choices=[
        ('general', 'General Discussion'),
        ('events', 'Community Events'),
        ('support', 'Support & Help'),
        ('ideas', 'Feature Requests')
    ], default='general')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_type = 'community'

# Comment model for all post types
class Comment(models.Model):
    content = models.TextField()
    post_id = models.IntegerField(null=True, blank=True)
    post_type = models.CharField(max_length=20, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.get_post().title if self.get_post() else 'Unknown Post'}"
    
    def get_post(self):
        """Get the actual post object based on type and id"""
        if not self.post_id or not self.post_type:
            return None
            
        if self.post_type == 'normal':
            return NormalPost.objects.get(id=self.post_id)
        elif self.post_type == 'announcement':
            return AnnouncementPost.objects.get(id=self.post_id)
        elif self.post_type == 'community':
            return CommunityPost.objects.get(id=self.post_id)
        return None
    
    def get_post_type(self):
        """Get the type of the post this comment belongs to"""
        return self.post_type

# Notification model for tracking interactions
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
        ('announcement', 'Announcement')
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    post = models.ForeignKey('NormalPost', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} notification from {self.actor.username} to {self.recipient.username}"
