
from django.forms.models import model_to_dict

import jwt
from django.utils import timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
import threading


User = get_user_model()




def check_authenticated(headers: dict) -> bool:

    return False


def return_user_roles(headers: dict):

    return ()


def get_user_profile(user_id, json=False):

    user = User.objects.get(pk=user_id)
    
    if json:
        return model_to_dict(user, fields='__all__')
    return user


def validate_user_password(password: str, user = None) -> str:
    """
    Validate a password using Django's built-in password validators and
    raise a DRF ValidationError with friendly messages if it fails.
    """
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        message = " ".join(exc.messages)
        raise serializers.ValidationError(message)
    return password


def generate_access_token(user: AbstractUser):
    payload = {
        'user_id': str(user.id),
        'role': user.user_type,
        'exp': timezone.now() + timezone.timedelta(days=1),
        'iat': timezone.now(),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user: AbstractUser):
    payload = {
        'user_id': str(user.id),
        'exp': timezone.now() + timezone.timedelta(days=7),
        'iat': timezone.now(),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def refresh_access_token(refresh_token):
    """ Refresh the access token using the refresh token."""
    if not refresh_token:
        raise AuthenticationFailed('Refresh token is required to get new access token.')
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Invalid refresh token.')

        user = User.objects.get(id=user_id)
        if not user.is_active:
            raise AuthenticationFailed('User is inactive.')
    except Exception as e:
        print(f"Error decoding refresh token: {e}")

    data={
        'access':generate_access_token(user),
        'refresh': refresh_token
        }
    return data



    