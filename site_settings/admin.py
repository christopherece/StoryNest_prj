from django.contrib import admin
from .models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('logo_name', 'logo', 'favicon')
    fieldsets = (
        (None, {
            'fields': ('logo', 'logo_name', 'favicon')
        }),
    )
    
    def has_add_permission(self, request):
        # Only one instance of SiteSettings should exist
        return not SiteSettings.objects.exists()
