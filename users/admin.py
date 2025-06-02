from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Kid

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'image_tag')
    search_fields = ('user__username', 'bio')
    
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return format_html('<img src="{}" width="50" height="50" />', obj.image_url)
    image_tag.short_description = 'Profile Picture'

@admin.register(Kid)
class KidAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'age', 'date_of_birth', 'profile_picture_tag')
    list_filter = ('parent',)
    search_fields = ('name', 'parent__username')
    readonly_fields = ('created_at', 'age')
    
    def profile_picture_tag(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_picture.url)
        return format_html('<img src="{}" width="50" height="50" />', obj.profile_picture_url)
    profile_picture_tag.short_description = 'Profile Picture'

    def age(self, obj):
        return obj.age
    age.short_description = 'Age'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Add annotations for age calculation
        return queryset
