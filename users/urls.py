from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.user_profile, name='user-profile'),
]
