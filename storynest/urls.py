"""
URL configuration for StoryNest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from storynest import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import welcome_view
from posts.views_pages import about_view, privacy_view, terms_view

# Customize the admin site
admin.site.site_header = 'LoopedIn Administration'
admin.site.site_title = 'LoopedIn Admin'
admin.site.index_title = 'Site Administration'

urlpatterns = [
    path('', welcome_view, name='welcome'),  # Welcome page for unauthenticated users
    path('home/', include('posts.urls')),    # Posts app URLs moved to /home/
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html', http_method_names=['get', 'post']), name='logout'),
    path('register/', include('users.urls')),
    path('chat/', include('chat.urls')),
    # Pages
    path('about/', about_view, name='about'),
    path('privacy/', privacy_view, name='privacy'),
    path('terms/', terms_view, name='terms'),
]

# Serve media files in any environment
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files even in production for the admin site
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Explicitly serve admin static files
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

# Add explicit paths for admin static files
from django.views.static import serve
import django
django_path = django.__path__[0]

# Always add these URL patterns to ensure admin static files are served correctly
urlpatterns += [
    # Direct admin static file paths
    path('admin/css/<path:path>', serve, {
        'document_root': django_path + '/contrib/admin/static/admin/css/'
    }),
    path('admin/js/<path:path>', serve, {
        'document_root': django_path + '/contrib/admin/static/admin/js/'
    }),
    path('admin/img/<path:path>', serve, {
        'document_root': django_path + '/contrib/admin/static/admin/img/'
    }),
    # For nav_sidebar.js specifically
    path('admin/js/nav_sidebar.js', serve, {
        'document_root': django_path + '/contrib/admin/static/admin/js/',
        'path': 'nav_sidebar.js'
    }),
    # Catch-all for other admin static files
    path('admin/<path:path>', lambda request, path: serve(request, path, document_root=django_path + '/contrib/admin/static/admin/') if path.startswith(('css/', 'js/', 'img/')) else admin.site.urls(request, path)),
]
