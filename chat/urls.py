from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='chat-inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='chat-conversation'),
    path('start/<str:username>/', views.start_conversation, name='chat-start'),
    path('api/conversation/<int:conversation_id>/send/', views.send_message_ajax, name='chat-send-message-ajax'),
    path('api/conversation/<int:conversation_id>/messages/<int:last_message_id>/', views.get_new_messages_ajax, name='chat-get-new-messages'),
    path('api/unread-count/', views.unread_message_count, name='chat-unread-count'),
]
