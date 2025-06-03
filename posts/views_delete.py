from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from .models import BasePost, AnnouncementPost, CommunityPost, NormalPost

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
        return reverse('home')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Post has been deleted successfully.')
        return redirect(success_url)
