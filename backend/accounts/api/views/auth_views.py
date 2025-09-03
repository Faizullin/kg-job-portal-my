from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounts.api.serializers import LogoutResponseSerializer
from accounts.models import LoginSession
# Utility functions replaced with direct Response objects


class LogoutView(generics.GenericAPIView):
    """User logout view - enhanced version of api_users LogOutView"""
    serializer_class = LogoutResponseSerializer
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
        
        response_data = {'message': 'Logged out successfully'}
        serializer = self.get_serializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
