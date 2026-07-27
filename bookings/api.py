from django.apps import apps
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from bookings.serializers import AppointmentsSerializer


class AppointmentsView(ModelViewSet):
    model = apps.get_model('bookings', 'AppointmentsModel')
    serializer_class = AppointmentsSerializer
    queryset = model.objects.all()
    search_fields = ['start_time', ]

    class_path = 'appointments'


    def get_queryset(self):
        # all if admin
        # by doc if doc
        # by public if public
        return self.queryset.filter()

    
                
