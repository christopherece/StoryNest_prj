from .models import SiteConfig

def site_config(request):
    config = SiteConfig.objects.first()
    if not config:
        config = SiteConfig.objects.create(
            logo_name='LoopedIn',
            welcome_title='Welcome to LoopedIn',
            welcome_subtitle='Connect with friends and share your experiences',
            sign_in_text='Sign in to access your feed, connect with friends, and more.',
            register_text='Join our community today and start sharing your experiences.',
            connect_heading='Connect',
            connect_description='Find and connect with friends, family, and like-minded individuals.',
            share_heading='Share',
            share_description='Share your thoughts, photos, and experiences with your network.',
            learn_heading='Learn',
            learn_description='Discover new opportunities and grow your professional network.'
        )
    
    return {
        'site_config': config,
        'welcome_content': config  # Same as site_config since they're combined
    }
