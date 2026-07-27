
import threading
from django.conf import settings

import jwt
from django.conf import settings

_request_local = threading.local()



def decode_jwt(jwt_code):
	response = jwt.decode(jwt_code, settings.SECRET_KEY, algorithms='HS256', options={"verify_signature": True, "verify_exp": True})
	return response


def get_current_request():
	return getattr(_request_local, 'request', None)

