
import uuid

from django.db import models

from utils.auth_utils import decode_jwt, get_current_request
from utils.exceptions import SuspiciousActivityDetectedError

import datetime
from django.db import models


class GenericModelManager(models.Manager):
	def create(self, **kwargs):
		if 'created_by' not in kwargs:
			actor = GenericBaseModel.get_current_actor()
			if actor:
				kwargs['created_by'] = actor
		kwargs['deleted_by'] = None
		created_instance = super().create(**kwargs)
		return created_instance
	
	def get_queryset(self):
		# Filter out deleted records
		return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
	"""Manager that returns all records, including deleted ones."""
	
	def get_queryset(self):
		return super().get_queryset()

class GenericPrimaryKeyField(models.UUIDField):
    def __init__(self, **kwargs):
        kwargs.setdefault('primary_key', True)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('default', uuid.uuid4)
        kwargs.setdefault('unique', True)
        super().__init__(**kwargs)

class GenericBaseModel(models.Model):
	id = GenericPrimaryKeyField()
	date_created = models.DateTimeField(auto_now_add=True)
	created_by = models.CharField(max_length=255, null=True, blank=True)
	last_modified = models.DateTimeField(auto_now=True)
	is_deleted = models.BooleanField(default=False)
	date_deleted = models.DateTimeField(null=True, blank=True)
	deleted_by = models.CharField(max_length=255, null=True, blank=True)
	
	class Meta:
		abstract = True
	
	objects = GenericModelManager()
	objects_all = AllObjectsManager()
	
	def delete(self, using=None, keep_parents=False):
		# no deletion allowed
		raise SuspiciousActivityDetectedError("Action flagged as fraudulent. Deletion not allowed.")
	

	@staticmethod
	def get_current_actor():
		request = get_current_request()
		if request:
			user = decode_jwt(request.headers.get('JWTAUTH').split(' ')[1])
			return user
		return None


