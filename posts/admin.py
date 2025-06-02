from django.contrib import admin
from .models import Post, Comment, Announcement, Notification

# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'is_active', 'created_by')
    list_filter = ('is_active', 'event_date')
    search_fields = ('title', 'content')
    date_hierarchy = 'event_date'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new announcement
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'actor', 'post', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'actor__username', 'post__title')
    date_hierarchy = 'created_at'
