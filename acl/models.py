from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.base_models import GenericBaseModel


class CustomUser(AbstractUser, GenericBaseModel):
    ROLES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('public', 'public'),
    )

    GENDER=(
        ('male','Male'),
        ('female','Female'),
        ('other',"Rather Not say")
    )
    first_name=models.CharField(max_length=100,blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    other_names = models.CharField(max_length=255, blank=True, null=True)
    
    user_type = models.CharField(max_length=10, choices=ROLES, blank=False,default='public')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth=models.DateField(blank=True, null=True)
    gender=models.CharField(max_length=20,choices=GENDER,blank=True,null=True)

    residence = models.TextField(blank=True, null=True)

    # for doctors, check if fulltime or locum; all fulltime now

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']


