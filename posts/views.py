from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.sessions.models import Session
from .models import Post, Comment, Announcement, Notification
from django.contrib.auth.models import User
from django.contrib import messages

# Home view to display all posts
class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 5
    login_url = 'login'  # Redirect to login page if not authenticated
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get upcoming active announcements
        context['announcements'] = Announcement.objects.filter(
            is_active=True,
            event_date__gte=timezone.now()
        ).order_by('event_date')[:5]  # Limit to 5 upcoming events
        
        # Get currently logged in users (users with active sessions)
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        logged_in_user_ids = []
        
        # Extract user IDs from session data
        for session in active_sessions:
            data = session.get_decoded()
            user_id = data.get('_auth_user_id')
            if user_id:
                logged_in_user_ids.append(int(user_id))
        
        # Get all users who are currently logged in
        active_users = User.objects.filter(id__in=logged_in_user_ids).order_by('-last_login')[:10]  # Top 10 logged in users
        
        # Mark all as online and add post count
        for user in active_users:
            user.is_online = True
            user.post_count = Post.objects.filter(author=user).count()
        
        context['active_users'] = active_users
        
        # Add unread notifications count for the current user
        if self.request.user.is_authenticated:
            context['unread_notifications_count'] = Notification.objects.filter(
                recipient=self.request.user,
                is_read=False
            ).count()
            
        return context

# User's posts view
class UserPostListView(ListView):
    model = Post
    template_name = 'posts/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['user_profile'] = user.profile
        return context

# Post detail view
class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        return context

# Create post view
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'posts/post_form.html'
    fields = ['title', 'content', 'image']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        # Check if this is a modal submission
        if request.POST.get('from_modal') == 'true':
            form = self.get_form()
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                messages.success(request, 'Your post has been created!')
                return redirect('home')
            else:
                # If form is invalid, return to home with error message
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                return redirect('home')
        # Otherwise process as normal
        return super().post(request, *args, **kwargs)

# Update post view
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'posts/post_form.html'
    fields = ['title', 'content', 'image']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

# Delete post view
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('home')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

# Add comment to post
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Create the comment
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            
            # Create notification for post owner (if not the same as comment author)
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    notification_type='comment',
                    actor=request.user,
                    post=post
                )
                
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty!')
    
    return redirect('post-detail', pk=pk)

# Like/unlike post
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
        
        # Remove any existing like notification
        Notification.objects.filter(
            recipient=post.author,
            notification_type='like',
            actor=request.user,
            post=post
        ).delete()
    else:
        post.likes.add(request.user)
        liked = True
        
        # Create notification for post owner (if not the same as like author)
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                notification_type='like',
                actor=request.user,
                post=post
            )
    
    return JsonResponse({
        'liked': liked,
        'count': post.get_like_count()
    })

# Notifications view
@login_required
def notifications(request):
    # Get all notifications for the current user
    notifications_list = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Mark all as read if requested
    if request.GET.get('mark_all_read'):
        notifications_list.update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')
    
    return render(request, 'posts/notifications.html', {'notifications': notifications_list})

# Mark notification as read
@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # Redirect to the post that the notification is about
    return redirect('post-detail', pk=notification.post.pk)

# AJAX endpoint to mark notification as read
@login_required
def mark_notification_read_ajax(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
