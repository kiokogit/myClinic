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
        qs = self.queryset
        # all if admin
        if self.request.user.user_type == 'public':
            qs = qs.filter(patient=self.request.user)
        elif self.request.user.user_type == 'doctor':
            qs = qs.filter(doctor=self.request.user)
        return qs

    
                
