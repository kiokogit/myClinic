from datetime import datetime, timedelta
from rest_framework.decorators import action
from django.apps import apps
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from bookings.models import AppointmentsModel
from hrm.models import DoctorsWorkScheduleModel, UserUnavailabilityModel
from hrm.serializers import WorkScheduleSerializer
from hrm.services import AvailabilityService


class UserAvailabilityViewSet(ModelViewSet):
    model = apps.get_model('hrm', 'DoctorsWorkScheduleModel')
    serializer_class = WorkScheduleSerializer
    queryset = model.objects.all()
    search_fields = ['doctor__first_name', 'doctor__last_name', 'start_date', ]

    class_path = 'doctor-schedules'


    def get_queryset(self):
        
        return self.queryset


    @action(detail=False, methods=['get'])
    def availability(self, request):
       available_slots = AvailabilityService().get_doctor_available_slots(
           doc_id=self.request.query_params.get('d_id', None),  # type: ignore
           book_date=self.request.query_params.get('date') # type: ignore
       )
       return Response({"available_slots": available_slots})