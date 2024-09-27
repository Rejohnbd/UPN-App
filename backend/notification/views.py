from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Notification, NotificationSetting
from .serializers import NotificationSerializer
from datetime import datetime, timedelta
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
import json


# Define the path to the service account JSON file
SERVICE_ACCOUNT_FILE = './notiyapp-ed846-firebase-adminsdk-3p7i6-fbbc786c9a.json'

# Initialize credentials from the service account file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/cloud-platform'],
)

# Helper function to get the Firebase access token
def get_access_token():
    credentials.refresh(Request())  # Refresh the access token
    return credentials.token

# Helper function to send a notification to Firebase Cloud Messaging (FCM)
def send_fcm_notification(access_token):
    url = 'https://fcm.googleapis.com/v1/projects/notiyapp-ed846/messages:send'  # FCM URL

    # Define the notification message payload
    message = {
        'message': {
            'topic': 'face_detection',
            'notification': {
                'title': 'Caution',
                'body': 'Unknown Face Detected'
            },
            "android": {
                "priority": "high"
            }
        }
    }

    # Define the request headers
    headers = {
        'Authorization': f'Bearer {access_token}',  # Authorization with access token
        'Content-Type': 'application/json'
    }

    # Send the POST request to FCM
    response = requests.post(url, headers=headers, data=json.dumps(message))

    # Check if the notification was successfully sent
    if response.status_code == 200:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification. Status code: {response.status_code}")

# Helper function to check if the interval between notifications is met
def can_send_notification(post_datetime, last_notification, interval):
    if last_notification:
        # Combine last notification's date and time into a datetime object
        last_notification_datetime = datetime.combine(last_notification.date, last_notification.time)

        # Calculate the time difference in minutes
        time_difference = (post_datetime - last_notification_datetime).total_seconds() / 60

        # Return True if the time difference is greater than the interval, else False
        return time_difference >= interval
    return True  # If no last notification exists, we can send a new one

# API view to handle notification creation
@api_view(['POST'])
def create_notification(request):
    # Retrieve the notification interval setting
    notification_setting = NotificationSetting.objects.first()
    if not notification_setting:
        return Response({'error': 'Notification settings not found.'}, status=status.HTTP_404_NOT_FOUND)

    interval = notification_setting.interval  # Get the interval value

    # Retrieve the last notification from the database
    last_notification = Notification.objects.last()

    # Get the date and time from the POST request
    post_date = request.data.get('date')
    post_time = request.data.get('time')

    try:
        # Combine the date and time from the request into a datetime object
        post_datetime = datetime.strptime(f"{post_date} {post_time}", '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return Response({'error': 'Invalid date or time format.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the interval condition is met before sending the notification
    if not can_send_notification(post_datetime, last_notification, interval):
        # If interval not met, calculate the remaining wait time
        last_notification_datetime = datetime.combine(last_notification.date, last_notification.time)
        remaining_time = (last_notification_datetime + timedelta(minutes=interval)) - post_datetime
        remaining_minutes = remaining_time.total_seconds() / 60
        return Response({'error': f'Please wait {remaining_minutes:.2f} more minutes before sending another notification.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # If interval condition is met, validate and save the new notification
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Save the notification to the database

        # Get the access token and send the notification via FCM
        access_token = get_access_token()
        send_fcm_notification(access_token)

        # Return a success response
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Return validation errors if the serializer is not valid
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
