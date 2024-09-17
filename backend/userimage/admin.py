from django.contrib import admin
from .models import UserImage

# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image')
    fields = ('user', 'image')

admin.site.register(UserImage, UserProfileAdmin)