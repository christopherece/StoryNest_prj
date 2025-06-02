from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def welcome_view(request):
    """
    Display welcome page for unauthenticated users.
    If user is already authenticated, redirect to home page.
    """
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'welcome.html')
