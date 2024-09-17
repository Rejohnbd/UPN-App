import requests
from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import UserImage
from django.conf import settings

# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image')
    fields = ('user', 'image')

    def save_model(self, request, obj, form, change):
        """
        Override save_model to post the image to an external API after saving the object.
        """
        super().save_model(request, obj, form, change)

        # After saving the image, post it to an external API
        if obj.image:
            image_path = obj.image.path  # Path to the saved image
            api_url = settings.EXTERNAL_API_URL + '/upload' 
            
            # Send the image to the API
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                response = requests.post(api_url, files=files)

            # Check API response status
            if response.status_code == 200:
                self.message_user(request, "Image uploaded and posted to the API successfully.")
            else:
                self.message_user(request, "Failed to post the image to the API.", level='error')
    
    def response_change(self, request, obj):
        """
        Override response_change to redirect back to the image list view after an update.
        """
        # Redirect to the UserImage list view in admin
        if "_continue" not in request.POST:
            return HttpResponseRedirect(reverse('admin:userimage_userimage_changelist'))
        else:
            return super().response_change(request, obj)


admin.site.register(UserImage, UserProfileAdmin)