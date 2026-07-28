from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from django.apps import apps
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
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


    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='date', 
                type=OpenApiTypes.STR, 
                location=OpenApiParameter.QUERY, 
                description='Choose the date to check availability',
                required=True,
            ),
        ],
        request={},                
        description="Check slots where a doctor is available",
        tags=["hrm"],                               
    )
    @action(detail=True, methods=['get'], url_path="availability")
    def availability(self, request, pk=None):
       available_slots = AvailabilityService().get_doctor_available_slots(
           doc_id=pk,
           book_date=self.request.query_params.get('date') # type: ignore
       )
       return Response({"available_slots": available_slots})

    