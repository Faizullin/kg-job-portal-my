import logging
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)


class CustomTokenAuthentication(TokenAuthentication):
    """
    Custom token authentication that prints request headers for debugging.
    Similar to default JWT but with header logging functionality.
    """
    
    def authenticate(self, request):
        """
        Authenticate using token and print headers for debugging.
        """
        # Print headers for debugging
        # self._print_headers(request)
        
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not (auth_header.startswith('Token ') or auth_header.startswith('Bearer ')):
            return None
        
        token_key = auth_header.split(' ')[1]
        
        try:
            # Get token object
            token = Token.objects.select_related('user').get(key=token_key)
            
            # Check if user is active and not blocked
            if not token.user.is_active:
                # print(f"Inactive user attempted authentication: {token.user.email}")
                return None
            
            if hasattr(token.user, 'blocked') and token.user.blocked:
                # print(f"Blocked user attempted authentication: {token.user.email}")
                return None
            
            return (token.user, token) 
            
        except Token.DoesNotExist:
            # print(f"Invalid token attempted: {token_key[:10]}...")
            return None
    
    def _print_headers(self, request):
        """
        Print request headers for debugging purposes.
        """
        print("=== AUTH HEADERS DEBUG ===")
        print(f"Method: {request.method} | Path: {request.path}")
        
        # Print key headers
        auth_header = request.META.get('HTTP_AUTHORIZATION', 'Not provided')
        user_agent = request.META.get('HTTP_USER_AGENT', 'Not provided')
        content_type = request.META.get('CONTENT_TYPE', 'Not provided')
        
        print(f"Authorization: {auth_header}")
        print(f"User-Agent: {user_agent}")
        print(f"Content-Type: {content_type}")
        print("=== END AUTH HEADERS DEBUG ===")
