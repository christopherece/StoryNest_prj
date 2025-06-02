from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class SiteConfig(models.Model):
    # Site Branding
    logo = models.ImageField(
        upload_to='site_config/', 
        null=True, 
        blank=True,
        help_text='Upload the site logo (30x30px recommended)'
    )
    logo_name = models.CharField(
        max_length=50, 
        default='LoopedIn',
        help_text='Name of your site'
    )
    favicon = models.ImageField(
        upload_to='site_config/', 
        null=True, 
        blank=True,
        help_text='Upload a favicon (16x16px recommended)'
    )
    
    # Welcome Page Content
    welcome_title = models.CharField(
        max_length=100, 
        default='Welcome to LoopedIn',
        help_text='Main welcome page title'
    )
    welcome_subtitle = models.CharField(
        max_length=200, 
        default='Connect with friends and share your experiences',
        help_text='Welcome page subtitle text'
    )
    
    sign_in_text = models.CharField(
        max_length=200, 
        default='Already have an account? Sign in to access your feed, connect with friends, and more.',
        help_text='Text for the sign in section'
    )
    register_text = models.CharField(
        max_length=200, 
        default='New here? Join our community today and start sharing your experiences.',
        help_text='Text for the register section'
    )
    
    connect_heading = models.CharField(
        max_length=50, 
        default='Connect',
        help_text='Heading for the connect feature'
    )
    connect_description = models.TextField(
        default='Find and connect with friends, family, and like-minded individuals.',
        help_text='Description for the connect feature'
    )
    
    share_heading = models.CharField(
        max_length=50, 
        default='Share',
        help_text='Heading for the share feature'
    )
    share_description = models.TextField(
        default='Share your thoughts, photos, and experiences with your network.',
        help_text='Description for the share feature'
    )
    
    learn_heading = models.CharField(
        max_length=50, 
        default='Learn',
        help_text='Heading for the learn feature'
    )
    learn_description = models.TextField(
        default='Discover new opportunities and grow your professional network.',
        help_text='Description for the learn feature'
    )
    
    def __str__(self):
        return self.logo_name
    
    @classmethod
    def get_default_content(cls):
        """Get or create default welcome content"""
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls.objects.create(
                logo_name='LoopedIn',
                welcome_title='Welcome to LoopedIn',
                welcome_subtitle='Connect with friends and share your experiences',
                sign_in_text='Already have an account? Sign in to access your feed, connect with friends, and more.',
                register_text='New here? Join our community today and start sharing your experiences.',
                connect_heading='Connect',
                connect_description='Find and connect with friends, family, and like-minded individuals.',
                share_heading='Share',
                share_description='Share your thoughts, photos, and experiences with your network.',
                learn_heading='Learn',
                learn_description='Discover new opportunities and grow your professional network.'
            )
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if self.pk is None:
            try:
                existing = SiteConfig.objects.get()
                self.pk = existing.pk
            except SiteConfig.DoesNotExist:
                pass
        super().save(*args, **kwargs)
