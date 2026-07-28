from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from acl.utils import generate_access_token, generate_refresh_token


# Create your views here.

User = get_user_model()


class GeneralUserService:

    def login(self, data):
        try:
            user = User.objects.get(username__iexact=data.get('username'))
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid email/password.")
        except User.MultipleObjectsReturned:
            raise AuthenticationFailed("Your account could not be verified. Please contact support.")

        if not user.check_password(data.get('password')):
            raise AuthenticationFailed("Invalid user credentials. Please try again.")

        user.last_login = timezone.now()
        user.save()

        # generate tokens

        return {
            'access': generate_access_token(user), # type:ignore
            'refresh': generate_refresh_token(user) # type:ignore
        }




