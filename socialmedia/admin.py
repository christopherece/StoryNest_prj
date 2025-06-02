from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.contrib.auth.models import User, Group
from users.models import Profile
from posts.models import Post, Comment, Notification, Announcement
from chat.models import Message, ChatRoom

class LoopedInAdminSite(AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = _('LoopedIn Admin')

    # Text to put in each page's <h1>.
    site_header = _('LoopedIn Administration')

    # Text to put at the top of the admin index page.
    index_title = _('Site Administration')

    # URL for the "View site" link at the top of each admin page.
    site_url = '/'

# Create an instance of the custom admin site
loopedin_admin_site = LoopedInAdminSite(name='loopedin_admin')

# Register models with our custom admin site
loopedin_admin_site.register(User)
loopedin_admin_site.register(Group)
loopedin_admin_site.register(Profile)
loopedin_admin_site.register(Post)
loopedin_admin_site.register(Comment)
loopedin_admin_site.register(Notification)
loopedin_admin_site.register(Announcement)
loopedin_admin_site.register(Message)
loopedin_admin_site.register(ChatRoom)

# Replace the default admin site with our custom one
admin.site = loopedin_admin_site
