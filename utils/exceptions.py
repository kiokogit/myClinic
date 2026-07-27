"""
Define all exceptions here, for the project, that are common and can be defined
"""
import traceback
from rest_framework.views import Response, exception_handler
from datetime import datetime
from utils.exceptions_defs import *

from django.apps import apps
import logging


logger = logging.getLogger(__name__)

_log_model = None


def get_log_model():
	"""Lazy load the DataChangesAndSuspectedActivity model"""
	global _log_model
	if _log_model is None:
		try:
			# Replace 'ardhi_framework' with your actual app name if different
			_log_model = apps.get_model('system', 'DataChangesAndSuspectedActivity')
		except LookupError:
			# Model not found, you might want to handle this differently
			logger.error("DataChangesAndSuspectedActivity model not found")
			return None
	return _log_model


# Custom exception handler for DRF
def custom_exception_handler(exc, context):
	"""
	Custom exception handler that handles ArdhiException properly
	"""
	tb_ = traceback.format_exc()
	logging.error(traceback.print_exc())
	if isinstance(exc, CustomException):
		return exc.to_response(tb_)
	response = exception_handler(exc, context)
	if response is not None:
		return response
	return CustomException().to_response(tb_)


def log_activity(data, description, activity_type='FAILED_EVENTS', source='USER', tb_=None):
	"""Helper method to log activity with error handling"""
	try:
		log_model = get_log_model()
		if log_model:
			log_model.objects.create(
				data=data,
				description=description,
				activity_type=activity_type,
				source=source,
				traceback=tb_
			)
	except Exception as e:
		logger.error(f"Failed to log activity: {e}")


class CustomException(Exception):
	"""Base exception for microservices errors"""
	default_status_code = 400
	default_message = 'Unknown error has occurred.'
	
	def __init__(self, message=None, status_code=None):
		super().__init__(message)
		self.message = message if bool(message) else self.default_message
		self.status_code = status_code or self.default_status_code
	
	def to_response(self, tb_=None):
		logging.error(self.message)
		"""Convert exception to Django JsonResponse"""
		log_activity(
			data={"details": f"{self.message} (Error {self.status_code}). ", "timestamp": datetime.now().isoformat()},
			description=f'Error while executing a request',
			tb_=tb_
		)
		return Response(
			{"details": f"{self.message} (Error {self.status_code})"},
			status=self.status_code
		)


class SuspiciousActivityDetectedError(CustomException):
	default_message = 'Action terminated prematurely.'
	default_status_code = SUSPICIOUS_ACTIVITY_ERROR_CODE


class UnauthorizedActorError(CustomException):
	default_message = 'You are not authorized to perform that action at this time.'
	default_status_code = UNAUTHORIZED_ACTOR_CODE


class TimeoutError(CustomException):
	"""This is when there is a timeout in any request"""
	default_message = "The server could not generate the expected response in time."
	default_status_code = TIMEOUT_SLOW_QUERY_ERROR_CODE


class DDOSProtectionError(CustomException):
	default_message = "We have detected unusual activity in your account."
	default_status_code = TOO_MANY_REQUESTS_ERROR_CODE
	

class UserInputValidationError(CustomException):
	default_message = "Invalid user request. Please try again"
	default_status_code = USER_INPUT_ERROR_CODE
	