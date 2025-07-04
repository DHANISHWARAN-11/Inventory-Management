from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, PermissionDenied
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # If DRF didn't handle it, handle it generically
    if response is None:
        return Response({'detail': 'An unexpected error occurred.'}, status=500)

    # Customize known exceptions
    if isinstance(exc, NotAuthenticated):
        response.data = {'detail': 'Authentication token is missing.'}
    elif isinstance(exc, AuthenticationFailed):
        response.data = {'detail': 'Authentication token is invalid or expired.'}
    elif isinstance(exc, PermissionDenied):
        response.data = {'detail': 'You do not have the necessary permissions to perform this action.'}

    return response
