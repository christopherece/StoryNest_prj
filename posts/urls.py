from django.urls import path
from . import views
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView, UserPostListView
)

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('post/<int:pk>/like/', views.like_post, name='like-post'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read_ajax, name='mark-notification-read-ajax'),
]
