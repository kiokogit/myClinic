from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
import jwt
from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension




class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "utils.auth_classes.JWTAuthentication"  
    name = "BearerAuth"                                    

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token as: Bearer <token>",
        }

class JWTAuthentication(authentication.BaseAuthentication):                                   
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")

        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.NotAuthenticated()

        return self.authenticate_credentials(parts[1])

    def authenticate_credentials(self, token):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.NotAuthenticated()
        except jwt.InvalidTokenError as e:
            print(e)
            raise exceptions.NotAuthenticated()

        user_id = payload.get("user_id") or payload.get("id")
        if not user_id:
            raise exceptions.NotAuthenticated()

        User = get_user_model()       

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.NotAuthenticated()

        if not user.is_active:
            raise exceptions.NotAuthenticated()

        return (user, token)