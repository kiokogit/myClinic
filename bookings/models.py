
from django.db import models

from utils.base_models import GenericBaseModel

# Create your models here.


class AppointmentsModel(GenericBaseModel):
    public_user = models.ForeignKey('acl.CustomUser', related_name='bookings', on_delete=models.CASCADE)
    target_user = models.ForeignKey('acl.CustomUser', related_name='appointments', on_delete=models.CASCADE)

    start_time = models.DateTimeField(null=False)
    # assume duration is 30mins
    duration_in_minutes = models.SmallIntegerField(default=30)

    # this status is for public appointment status
    public_status = models.CharField(max_length=100, choices=[
        ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('COMPLETED', 'COMPLETED'), ('CANCELLED', 'CANCELLED')
        ], default='PENDING')
    # this status changes as per doctor's acceptance/in case of change of their availability
    # doctor_status = models.CharField(max_length=100, choices=[('PENDING', 'PENDING'), ('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED'), ('REQUESTED_RESCHEDULE', 'REQUESTED_RESCHEDULE')], default='PENDING')


