
import uuid

from django.db import models

from utils.auth_utils import decode_jwt, get_current_request
from utils.exceptions import SuspiciousActivityDetectedError

import datetime
from django.db import models


class GenericQuerySet(models.QuerySet):
	def delete(self):
		actor = GenericBaseModel.get_current_actor()
		return self.update(
			is_deleted=True,
			deleted_by=actor,
			is_active=False,
			date_deleted=datetime.datetime.now()
		)

class GenericModelManager(models.Manager):
	def create(self, **kwargs):
		kwargs.setdefault(
			"created_by",
			GenericBaseModel.get_current_actor()
		)
		kwargs["deleted_by"] = None
		kwargs["is_deleted"] = False
		return super().create(**kwargs)
	
	def get_queryset(self):
		return GenericQuerySet(self.model, using=self._db).filter(
			is_deleted=False
		)


class AllObjectsManager(models.Manager):
	"""Manager that returns all records, including deleted ones."""
	def get_queryset(self):
			return GenericQuerySet(
				self.model,
				using=self._db
			)

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
		self.is_deleted = True
		self.is_active = False
		self.date_deleted = datetime.datetime.now()
		self.deleted_by = self.get_current_actor()
		self.save(update_fields=["is_deleted", "deleted_by", "is_active", "date_deleted"])

	@staticmethod
	def get_current_actor():
		request = get_current_request()
		if request:
			return request.user
		return None


