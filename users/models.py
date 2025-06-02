from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.templatetags.static import static
from django.utils.html import mark_safe

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    @property
    def image_url(self):
        try:
            if self.image and hasattr(self.image, 'url'):
                return self.image.url
        except Exception:
            pass
        # Return the user-default.png image
        return static('img/user-default.png')
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile image if it's too large
        try:
            if self.image and hasattr(self.image, 'path'):
                img = Image.open(self.image.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
        except Exception as e:
            # Handle case where image file doesn't exist
            print(f"Error processing profile image: {e}")
            # Use a default placeholder instead of failing
