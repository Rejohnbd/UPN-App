import os
import requests
from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import UserImage
from django.conf import settings
from django.utils.html import format_html
from django.core.exceptions import ValidationError

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_tag')  # Display user and the image
    fields = ('user', 'image')

    def save_model(self, request, obj, form, change):
        """
        Override save_model to:
        - Validate the file format.
        - Rename the image to 'username.jpg'.
        - Replace older images if the same user uploads a new image.
        - Post the image to an external API after saving the object.
        """
        try:
            # Validate the image file format
            if obj.image and not obj.image.name.endswith('.jpg'):
                raise ValidationError("Only .jpg files are allowed.")

            # Rename the image to 'username.jpg'
            obj.image.name = f'{obj.user.username}.jpg'

            # Check if the file already exists and delete the old one
            old_image_path = obj.image.path
            if os.path.exists(old_image_path):
                os.remove(old_image_path)  # Remove the old image

            # Save the model
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
        
        except ValidationError as e:
            # Catch the validation error and display it in the Django admin interface
            self.message_user(request, f"Error: {e.message}", level='error')

    def image_tag(self, obj):
        """
        Display the image in the admin list view.
        """
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />'.format(obj.image.url))
        return 'No Image'

    image_tag.short_description = 'Profile Image'  # This will be the column name

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
