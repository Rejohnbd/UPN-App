from django.urls import path
from .views import create_notification

urlpatterns = [
    path('notifications/', create_notification, name='create_notification'),
]