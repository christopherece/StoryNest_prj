from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q, Count
from .models import Conversation, Message
from django.utils import timezone

@login_required
def inbox(request):
    """Show all conversations for the current user"""
    conversations = Conversation.objects.filter(participants=request.user)
    
    # Add unread message count for each conversation
    for conversation in conversations:
        conversation.unread_count = Message.objects.filter(
            conversation=conversation, 
            sender__in=conversation.participants.exclude(id=request.user.id),
            is_read=False
        ).count()
        
        # Get the other participant
        conversation.other_user = conversation.get_other_participant(request.user)
        
        # Get last message for preview
        last_message = conversation.get_last_message()
        conversation.last_message = last_message
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'chat/inbox.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """Show a specific conversation and its messages"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Security check: ensure the user is a participant
    if request.user not in conversation.participants.all():
        return redirect('chat-inbox')
    
    # Get the other participant
    other_user = conversation.get_other_participant(request.user)
    
    # We'll handle message creation and reading via AJAX only
    context = {
        'conversation': conversation,
        'other_user': other_user,
    }
    return render(request, 'chat/conversation.html', context)

@login_required
def start_conversation(request, username):
    """Start a new conversation with a user"""
    other_user = get_object_or_404(User, username=username)
    
    # Don't allow conversations with self
    if other_user == request.user:
        return redirect('chat-inbox')
    
    # Check if a conversation already exists between these users
    conversations = Conversation.objects.filter(participants=request.user).filter(participants=other_user)
    
    if conversations.exists():
        # Conversation exists, redirect to it
        return redirect('chat-conversation', conversation_id=conversations.first().id)
    else:
        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
        return redirect('chat-conversation', conversation_id=conversation.id)

@login_required
def send_message_ajax(request, conversation_id):
    """AJAX endpoint for sending messages"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Security check: ensure the user is a participant
        if request.user not in conversation.participants.all():
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'}, status=400)
        
        # Create new message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            is_read=False  # Explicitly set as unread for the recipient
        )
        
        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save()
        
        return JsonResponse({
            'status': 'success',
            'message_id': message.id,
            'message_content': message.content,
            'timestamp': message.created_at.strftime('%b %d, %Y, %I:%M %p'),
            'sender_id': request.user.id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def get_new_messages_ajax(request, conversation_id, last_message_id):
    """AJAX endpoint for polling new messages"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Security check: ensure the user is a participant
    if request.user not in conversation.participants.all():
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        # Convert last_message_id to integer
        last_message_id = int(last_message_id)
        
        # If last_message_id is 0, return all messages for initial load
        if last_message_id == 0:
            messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        else:
            # Otherwise, get only new messages with ID greater than last_message_id
            messages = Message.objects.filter(
                conversation=conversation,
                id__gt=last_message_id
            ).order_by('created_at')
        
        # Mark messages from others as read
        messages.exclude(sender=request.user).update(is_read=True)
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'sender': message.sender.username,
                'content': message.content,
                'timestamp': message.created_at.strftime('%b %d, %Y, %I:%M %p'),
                'sender_id': message.sender.id,
                'created_at': message.created_at.strftime('%b %d, %Y, %I:%M %p')
            })
        
        return JsonResponse({
            'status': 'success',
            'messages': messages_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def unread_message_count(request):
    """AJAX endpoint to get the count of unread messages"""
    # Get conversations where the user is a participant
    conversations = Conversation.objects.filter(participants=request.user)
    
    # Count unread messages from other participants
    unread_count = Message.objects.filter(
        conversation__in=conversations,
        sender__in=User.objects.exclude(id=request.user.id),
        is_read=False
    ).count()
    
    return JsonResponse({
        'unread_count': unread_count
    })
