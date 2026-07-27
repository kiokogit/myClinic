from django.db import models

from utils.base_models import GenericBaseModel

# Create your models here.

class UserUnavailabilityModel(GenericBaseModel):
    # this model is for storing special unavailability cases like a leave, or so, besides the normal work schedule
    doctor = models.ForeignKey('acl.CustomUser', related_name='unavailability', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    reason = models.TextField(null=True, blank=True)

    replacement_doctor = models.ForeignKey('acl.CustomUser', related_name='temporal_availability', on_delete=models.CASCADE)

    # THIS ALLOWS user / admin to cancel a status for a leave or absence
    status = models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('CANCELLED', 'CANCELLED')], max_length=100, default='ACTIVE')


class DoctorsWorkScheduleModel(GenericBaseModel):
    # this to provide work schedules for either all or one of them
    
    # limits times of day/night that a doctor, any doctor is available
    doctor = models.ForeignKey('acl.CustomUser', related_name='general_availability', on_delete=models.CASCADE)
    # schedule start date and end date
    start_date = models.DateField()
    end_date = models.DateField()

    # schedule timing per day/night
    day_start_time = models.TimeField()
    day_end_time = models.TimeField()

    remarks = models.TextField(null=True, blank=True)

