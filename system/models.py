from django.db import models

from utils.base_models import GenericBaseModel

# Create your models here.

class DataChangesAndSuspectedActivity(GenericBaseModel):
    data = models.JSONField(default=dict)
    description = models.TextField(null=True, blank=True)
    activity_type = models.CharField(max_length=1000, null=True, blank=True)
    source = models.CharField(max_length=1000, null=True, blank=True,
	                          help_text='System or user')  # this is where either the system has raised an error, or a request has been initiated consciously by user - such as data change
	
    traceback = models.TextField(null=True, blank=True)
