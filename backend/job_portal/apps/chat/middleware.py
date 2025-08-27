from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from accounts.models import UserModel

class JWTWebSocketAuthMiddleware(BaseMiddleware):
    """
    Simple middleware to authenticate WebSocket connections using DRF tokens.
    Extracts token from query string and validates it against the database.
    """
    
    async def __call__(self, scope, receive, send):
        # Get token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = {}
        
        if query_string:
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value
        
        token = query_params.get('token', '')
        
        if token:
            scope['user'] = await self.get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """Validate token and return user."""
        try:
            # Get user from token
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            
            # Check if user is active and not deleted
            if user.is_active and not getattr(user, 'is_deleted', False):
                return user
            
        except (Token.DoesNotExist, UserModel.DoesNotExist):
            pass
        
        return AnonymousUser()
