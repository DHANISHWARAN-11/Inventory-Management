# middleware.py
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

class JwtAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # You can add token-blocking logic here if needed
        response = self.get_response(request)
        return response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    # Handle AuthenticationFailed (invalid token or wrong credentials)
    if isinstance(exc, AuthenticationFailed):
        view = context.get('view')
        if isinstance(view, TokenObtainPairView):
            return Response({'detail': 'Invalid username or password.'}, status=401)
        else:
            return Response({'detail': 'Authentication token is invalid or expired.'}, status=401)

    # Handle missing token
    elif isinstance(exc, NotAuthenticated):
        return Response({'detail': 'Authentication token is missing.'}, status=401)

    # Handle permission denied
    elif isinstance(exc, PermissionDenied):
        return Response({'detail': 'You do not have the necessary permissions to perform this action.'}, status=403)

    # Catch-all for unhandled exceptions
    if response is None:
        return Response({'detail': 'An unexpected error occurred.'}, status=500)

    return response
