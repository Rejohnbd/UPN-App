from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

# import firebase_admin
# from firebase_admin import credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
import json

# Create your views here.
SERVICE_ACCOUNT_FILE = './notiyapp-ed846-firebase-adminsdk-3p7i6-fbbc786c9a.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/cloud-platform'],
)

def get_access_token():
    credentials.refresh(Request())
    print(credentials.token)
    return credentials.token

@api_view(['POST'])
def create_notification(request):
    # Get an access token
    access_token = get_access_token()
    # FCM url
    url = 'https://fcm.googleapis.com/v1/projects/notiyapp-ed846/messages:send'
    # message data
    message = {
        'message': {
            'topic': 'face_detection',
            'notification': {
                'title': 'Unknown Face Detected',
                'body': 'Unknown Face Detected'
            },
            "android": {
                "priority":"high"
            }
        }
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url,  headers=headers, data= json.dumps(message))



    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # return Response({'message': 'Data posted successfully', 'access_token': access_token,  'data': response.json()}, status=status.HTTP_200_OK)
