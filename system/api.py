from django.apps import apps
from rest_framework.viewsets import ModelViewSet

from system.serializers import SystemErrorsLogsSerializer
from utils.exceptions import SuspiciousActivityDetectedError


class UserAvailabilityViewSet(ModelViewSet):
    model = apps.get_model('system', 'DataChangesAndSuspectedActivity')
    serializer_class = SystemErrorsLogsSerializer
    queryset = model.objects.all()
    search_fields = ['activity_type', ]

    class_path = 'logs'


    def get_queryset(self):
        
        return self.queryset.distinct()

    def create(self, request, *args, **kwargs):
        raise SuspiciousActivityDetectedError("Permission Denied!")

    def update(self, request, *args, **kwargs):
        raise SuspiciousActivityDetectedError("Permission Denied!")

    def destroy(self,  request, *args, **kwargs):
        raise SuspiciousActivityDetectedError("Permission Denied!")

