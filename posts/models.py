from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from PIL import Image

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.FileField(upload_to='post_media', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    @property
    def image_url(self):
        try:
            if self.image and hasattr(self.image, 'url'):
                return self.image.url
        except Exception:
            pass
        return None
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
    
    def get_like_count(self):
        return self.likes.count()
        
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
            # Handle case where image file doesn't exist
            print(f"Error processing post image: {e}")
            # Continue without failing

# Comment model for users to comment on posts
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

# Announcement/Event model for admins to create events
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['event_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_past_event(self):
        return self.event_date < timezone.now()

# Notification model for tracking interactions
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.actor.username} {self.notification_type}d your post "{self.post.title}"'
