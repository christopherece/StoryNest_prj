from django.shortcuts import render

def about_view(request):
    """View for the About page"""
    return render(request, 'pages/about.html')

def privacy_view(request):
    """View for the Privacy Policy page"""
    return render(request, 'pages/privacy.html')

def terms_view(request):
    """View for the Terms of Service page"""
    return render(request, 'pages/terms.html')
