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
from .models import (
    BasePost, NormalPost, AnnouncementPost, CommunityPost,
    Comment, Notification
)
from .forms import NormalPostForm, AnnouncementPostForm, CommunityPostForm
from django.contrib.auth.models import User
from django.contrib import messages

# Home view to display all posts
class PostListView(LoginRequiredMixin, ListView):
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    paginate_by = 5
    login_url = 'login'  # Redirect to login page if not authenticated
    
    def get_queryset(self):
        # Get all posts, ordered by creation date
        normal_posts = NormalPost.objects.all()
        announcement_posts = AnnouncementPost.objects.all()
        community_posts = CommunityPost.objects.all()
        
        # Combine and sort all posts
        all_posts = list(normal_posts) + list(announcement_posts) + list(community_posts)
        all_posts.sort(key=lambda x: x.created_at, reverse=True)
        
        return all_posts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get upcoming active announcements
        context['announcements'] = AnnouncementPost.objects.filter(
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
            # Count posts for each type
            user.post_count = {
                'normal': NormalPost.objects.filter(author=user).count(),
                'announcement': AnnouncementPost.objects.filter(author=user).count(),
                'community': CommunityPost.objects.filter(author=user).count()
            }
        
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
    template_name = 'posts/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        # Get all posts for the user
        normal_posts = NormalPost.objects.filter(author=user)
        announcement_posts = AnnouncementPost.objects.filter(author=user)
        community_posts = CommunityPost.objects.filter(author=user)
        
        # Combine and sort all posts
        all_posts = list(normal_posts) + list(announcement_posts) + list(community_posts)
        all_posts.sort(key=lambda x: x.created_at, reverse=True)
        
        return all_posts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['user_profile'] = user.profile
        return context

# Post detail view
class PostDetailView(DetailView):
    template_name = 'posts/post_detail.html'
    
    def get_queryset(self):
        # Get the specific post type based on URL parameter
        post_type = self.kwargs.get('post_type')
        if post_type == 'normal':
            return NormalPost.objects.all()
        elif post_type == 'announcement':
            return AnnouncementPost.objects.all()
        elif post_type == 'community':
            return CommunityPost.objects.all()
        return None
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_type = self.kwargs.get('post_type')
        
        # Get comments using post_id and post_type
        context['comments'] = Comment.objects.filter(
            post_id=self.object.id,
            post_type=post_type
        ).order_by('-created_at')
        context['post_type'] = post_type
        context['post_type_display'] = self.object.get_post_type_display()
        return context
    
    def get_success_url(self):
        return reverse('home-post-detail', kwargs={'post_type': self.object.get_post_type(), 'pk': self.object.pk})
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        return obj

# Create post view
class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'posts/post_form.html'
    
    def get_form_class(self):
        post_type = self.kwargs.get('post_type')
        if post_type == 'announcement':
            return AnnouncementPostForm
        elif post_type == 'community':
            return CommunityPostForm
        return NormalPostForm
    
    def get_queryset(self):
        post_type = self.kwargs.get('post_type')
        if post_type == 'announcement':
            return AnnouncementPost.objects.all()
        elif post_type == 'community':
            return CommunityPost.objects.all()
        return NormalPost.objects.all()
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        messages.success(self.request, 'Your post has been created!')
        
        # Get the post_type from URL parameters
        post_type = self.kwargs.get('post_type')
        
        # Redirect to the correct post detail URL
        if post_type == 'announcement':
            return redirect('post-announcement-detail', pk=post.id, post_type='announcement')
        elif post_type == 'community':
            return redirect('post-community-detail', pk=post.id, post_type='community')
        return redirect('post-normal-detail', pk=post.id, post_type='normal')
    
    def get_success_url(self):
        # If this was a modal submission, redirect back to home
        if self.request.POST.get('from_modal'):
            return reverse('home')
        return super().get_success_url()

# Update post view
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BasePost
    template_name = 'posts/post_form.html'
    fields = ['title', 'content', 'image']
    
    def get_queryset(self):
        post_type = self.kwargs.get('post_type')
        if post_type == 'announcement':
            return AnnouncementPost.objects.all()
        elif post_type == 'community':
            return CommunityPost.objects.all()
        return NormalPost.objects.all()
    
    def get_object(self, queryset=None):
        post_type = self.kwargs.get('post_type')
        pk = self.kwargs.get('pk')
        if post_type == 'announcement':
            return get_object_or_404(AnnouncementPost, pk=pk)
        elif post_type == 'community':
            return get_object_or_404(CommunityPost, pk=pk)
        return get_object_or_404(NormalPost, pk=pk)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_success_url(self):
        return reverse('home-post-detail', kwargs={'post_type': self.object.get_post_type(), 'pk': self.object.pk})
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        messages.success(self.request, 'Your post has been updated!')
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

# Delete post view
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BasePost
    template_name = 'posts/post_confirm_delete.html'
    
    def get_queryset(self):
        post_type = self.kwargs.get('post_type')
        if post_type == 'announcement':
            return AnnouncementPost.objects.all()
        elif post_type == 'community':
            return CommunityPost.objects.all()
        return NormalPost.objects.all()
    
    def get_object(self, queryset=None):
        post_type = self.kwargs.get('post_type')
        pk = self.kwargs.get('pk')
        if post_type == 'announcement':
            return get_object_or_404(AnnouncementPost, pk=pk)
        elif post_type == 'community':
            return get_object_or_404(CommunityPost, pk=pk)
        return get_object_or_404(NormalPost, pk=pk)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_success_url(self):
        return reverse('home-post-detail', kwargs={'post_type': self.object.get_post_type(), 'pk': self.object.pk})

# Add comment to post
@login_required
def add_comment(request, pk, post_type):
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            messages.error(request, 'Comment cannot be empty!')
            return redirect('home-post-detail', pk=pk, post_type=post_type)
        
        if post_type == 'announcement':
            post = get_object_or_404(AnnouncementPost, pk=pk)
        elif post_type == 'community':
            post = get_object_or_404(CommunityPost, pk=pk)
        else:
            post = get_object_or_404(NormalPost, pk=pk)
        
        comment = Comment.objects.create(
            content=content,
            author=request.user,
            post_id=post.pk,
            post_type=post_type
        )
        
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                notification_type='comment',
                actor=request.user,
                post_id=post.pk,
                post_type=post_type,
                comment=comment
            )
        
        messages.success(request, 'Comment added successfully!')
        return redirect('home-post-detail', pk=pk, post_type=post_type)
    return redirect('home')

# Like/unlike post
@login_required
def like_post(request, pk, post_type):
    # Get the appropriate post model based on post_type
    if post_type == 'announcement':
        post = get_object_or_404(AnnouncementPost, pk=pk)
    elif post_type == 'community':
        post = get_object_or_404(CommunityPost, pk=pk)
    else:
        post = get_object_or_404(NormalPost, pk=pk)
    
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
