from django.contrib import admin
from .models import SiteConfig

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('logo_name', 'logo', 'favicon', 'welcome_title')
    fieldsets = (
        ('Site Branding', {
            'fields': ('logo', 'logo_name', 'favicon')
        }),
        ('Welcome Page Header', {
            'fields': ('welcome_title', 'welcome_subtitle')
        }),
        ('Sign In Section', {
            'fields': ('sign_in_text',)
        }),
        ('Register Section', {
            'fields': ('register_text',)
        }),
        ('Features', {
            'fields': ('connect_heading', 'connect_description',
                      'share_heading', 'share_description',
                      'learn_heading', 'learn_description')
        })
    )
    
    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()
