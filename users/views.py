from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, KidForm
from .models import Profile, Kid
from posts.models import NormalPost, AnnouncementPost, CommunityPost

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Authenticate and login the user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Account created for {username}! You are now logged in.')
                return redirect('home')
            else:
                messages.warning(request, f'Account created for {username}, but automatic login failed. Please log in manually.')
                return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile, user=request.user)
    
    # Pass the user to the template for user_type display
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_type': request.user.profile.user_type,
        'kids': request.user.kids.all(),
        'profile': request.user.profile
    }
    return render(request, 'users/profile.html', context)

@login_required
def add_kid(request):
    if request.method == 'POST':
        form = KidForm(request.POST, request.FILES)
        if form.is_valid():
            kid = form.save(commit=False)
            kid.parent = request.user
            kid.save()
            messages.success(request, f'Child {kid.name} has been added successfully!')
            return redirect('profile')
    else:
        form = KidForm()
    
    return render(request, 'users/add_kid.html', {'form': form})

@login_required
def update_kid(request, kid_id):
    kid = get_object_or_404(Kid, id=kid_id, parent=request.user)
    if request.method == 'POST':
        form = KidForm(request.POST, request.FILES, instance=kid)
        if form.is_valid():
            form.save()
            messages.success(request, f'Child {kid.name} has been updated successfully!')
            return redirect('profile')
    else:
        form = KidForm(instance=kid)
    
    return render(request, 'users/update_kid.html', {'form': form, 'kid': kid})

@login_required
def delete_kid(request, kid_id):
    kid = get_object_or_404(Kid, id=kid_id, parent=request.user)
    if request.method == 'POST':
        kid.delete()
        messages.success(request, f'Child {kid.name} has been removed successfully!')
        return redirect('profile')
    
    return render(request, 'users/delete_kid.html', {'kid': kid})

def user_profile(request, username):
    """View for viewing other users' profiles"""
    profile_user = get_object_or_404(User, username=username)
    
    # Get user's posts
    normal_posts = NormalPost.objects.filter(author=profile_user)
    announcement_posts = AnnouncementPost.objects.filter(author=profile_user)
    community_posts = CommunityPost.objects.filter(author=profile_user)
    
    # Combine and sort all posts
    all_posts = list(normal_posts) + list(announcement_posts) + list(community_posts)
    all_posts.sort(key=lambda x: x.created_at, reverse=True)
    posts = all_posts[:5]
    
    # Check if this is the current user's profile
    is_own_profile = request.user.is_authenticated and request.user == profile_user
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_own_profile': is_own_profile
    }
    return render(request, 'users/user_profile.html', context)
