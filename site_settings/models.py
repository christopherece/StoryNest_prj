from django.db import models
from django.contrib.auth.models import User

class SiteSettings(models.Model):
    logo = models.ImageField(upload_to='site_settings/', null=True, blank=True)
    logo_name = models.CharField(max_length=50, default='LoopedIn')
    favicon = models.ImageField(upload_to='site_settings/', null=True, blank=True)
    
    def __str__(self):
        return "Site Settings"
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if self.pk is None:
            try:
                existing = SiteSettings.objects.get()
                self.pk = existing.pk
            except SiteSettings.DoesNotExist:
                pass
        super().save(*args, **kwargs)
