from django.urls import path
from . import views
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView, UserPostListView
)

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    
    # Normal posts
    path('post/normal/<int:pk>/<str:post_type>/', PostDetailView.as_view(), name='post-normal-detail'),
    path('post/normal/new/<str:post_type>/', PostCreateView.as_view(), name='post-normal-create'),
    path('post/normal/<int:pk>/update/<str:post_type>/', PostUpdateView.as_view(), name='post-normal-update'),
    path('post/normal/<int:pk>/delete/<str:post_type>/', PostDeleteView.as_view(), name='post-normal-delete'),
    
    # Announcement posts
    path('post/announcement/<int:pk>/<str:post_type>/', PostDetailView.as_view(), name='post-announcement-detail'),
    path('post/announcement/new/<str:post_type>/', PostCreateView.as_view(), name='post-announcement-create'),
    path('post/announcement/<int:pk>/update/<str:post_type>/', PostUpdateView.as_view(), name='post-announcement-update'),
    path('post/announcement/<int:pk>/delete/<str:post_type>/', PostDeleteView.as_view(), name='post-announcement-delete'),
    
    # Community posts
    path('post/community/<int:pk>/<str:post_type>/', PostDetailView.as_view(), name='post-community-detail'),
    path('post/community/new/<str:post_type>/', PostCreateView.as_view(), name='post-community-create'),
    path('post/community/<int:pk>/update/<str:post_type>/', PostUpdateView.as_view(), name='post-community-update'),
    path('post/community/<int:pk>/delete/<str:post_type>/', PostDeleteView.as_view(), name='post-community-delete'),
    
    # Home page with post type
    path('home/post/<str:post_type>/', PostListView.as_view(), name='home-post'),
    path('home/post/<str:post_type>/<int:pk>/', PostDetailView.as_view(), name='home-post-detail'),
    path('home/post/<str:post_type>/new/', PostCreateView.as_view(), name='home-post-create'),
    path('home/post/<str:post_type>/<int:pk>/update/', PostUpdateView.as_view(), name='home-post-update'),
    path('home/post/<str:post_type>/<int:pk>/delete/', PostDeleteView.as_view(), name='home-post-delete'),
    
    # Comments and likes
    path('home/post/<str:post_type>/<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('home/post/<str:post_type>/<int:pk>/like/', views.like_post, name='like-post'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read_ajax, name='mark-notification-read-ajax'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read_ajax, name='mark-notification-read-ajax'),
]
