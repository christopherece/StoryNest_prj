from django.contrib import admin
from .models import NormalPost, AnnouncementPost, CommunityPost, Comment, Notification

# Register your models here.
admin.site.register(Comment)

@admin.register(AnnouncementPost)
class AnnouncementPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'is_active', 'author')
    list_filter = ('is_active', 'event_date')
    search_fields = ('title', 'content')
    date_hierarchy = 'event_date'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new announcement
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_sticky', 'author')
    list_filter = ('category', 'is_sticky')
    search_fields = ('title', 'content')
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new community post
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(NormalPost)
class NormalPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new post
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'actor', 'created_at', 'is_read')
    
    def get_post(self, obj):
        if obj.post_id:
            return f'{obj.post_type} #{obj.post_id}'
        return '-'
    get_post.short_description = 'Post'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'actor')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'actor__username', 'post__title')
    date_hierarchy = 'created_at'
