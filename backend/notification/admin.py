from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, NotificationSetting

# Register your models here.
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'image_preview')
    list_per_page = 10  # Number of items per page

    def image_preview(self, obj):
        if obj.image:
            # Create a link to the full-sized image
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="50" height="50" />'
                '</a>',
                obj.image.url,  # URL for the full-sized image
                obj.image.url   # URL for the thumbnail preview
            )
        return 'No Image'

    image_preview.short_description = 'Image'

admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationSetting)