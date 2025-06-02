from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('add-kid/', views.add_kid, name='add-kid'),
    path('kid/<int:kid_id>/update/', views.update_kid, name='update-kid'),
    path('kid/<int:kid_id>/delete/', views.delete_kid, name='delete-kid'),
    path('user/<str:username>/', views.user_profile, name='user-profile'),
]
