from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.templatetags.static import static
from django.utils.html import mark_safe
from django.utils import timezone

# Create your models here.

class UserType(models.TextChoices):
    PARENT = 'parent', 'Parent'
    TEACHER = 'teacher', 'Teacher'
    ADMIN = 'admin', 'Admin'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.PARENT)
    
    @property
    def image_url(self):
        try:
            if self.image and hasattr(self.image, 'url'):
                return self.image.url
        except Exception:
            pass
        # Return the user-default.png image
        return static('img/user-default.png')
    
    @property
    def is_parent(self):
        return self.user_type == UserType.PARENT
    
    @property
    def is_teacher(self):
        return self.user_type == UserType.TEACHER
    
    @property
    def is_admin(self):
        return self.user_type == UserType.ADMIN
    
    def __str__(self):
        return f'{self.user.username} Profile ({self.user_type})'
    
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

class Kid(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kids')
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    profile_picture = models.ImageField(upload_to='kid_pics', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name} (Parent: {self.parent.username})'
    
    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def profile_picture_url(self):
        try:
            if self.profile_picture and hasattr(self.profile_picture, 'url'):
                return self.profile_picture.url
        except Exception:
            pass
        # Return a default kid image
        return static('img/kid-default.png')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Rotate and resize kid's profile picture
        try:
            if self.profile_picture and hasattr(self.profile_picture, 'path'):
                img = Image.open(self.profile_picture.path)
                
                # Rotate image based on EXIF data if available
                try:
                    exif = img._getexif()
                    if exif:
                        orientation = exif.get(274)
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)
                except (AttributeError, KeyError, IndexError):
                    pass
                
                # Resize to square if needed
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    
                # Save the rotated and resized image
                img.save(self.profile_picture.path)
        except Exception as e:
            print(f"Error processing kid's profile picture: {e}")
