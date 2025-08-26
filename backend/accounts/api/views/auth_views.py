import uuid
from datetime import timedelta
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounts.api.serializers import FireBaseAuthSerializer
from accounts.models import LoginSession
# Utility functions replaced with direct Response objects


class FirebaseAuthView(generics.GenericAPIView):
    """Firebase authentication view - replaces api_users AuthViaFirebase"""
    serializer_class = FireBaseAuthSerializer
    permission_classes = []
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        
        # Firebase token verification and user creation/lookup logic
        # This will be implemented in the firebase_auth.py view
        return Response({'error': 'Use /auth/firebase/ endpoint for Firebase authentication'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    """User logout view - enhanced version of api_users LogOutView"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete Django token
        Token.objects.filter(user=request.user).delete()
        
        # Mark current session as inactive
        session_key = request.session.session_key
        if session_key:
            LoginSession.objects.filter(
                user=request.user,
                session_key=session_key,
                is_active=True
            ).update(
                is_active=False,
                logout_at=timezone.now()
            )
        
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
