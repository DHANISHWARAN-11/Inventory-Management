from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        token = request.COOKIES.get('jwt')
        if token:
            try:
                validated_token = self.jwt_auth.get_validated_token(token)
                user = self.jwt_auth.get_user(validated_token)
                request.user = user
            except Exception:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        return self.get_response(request)