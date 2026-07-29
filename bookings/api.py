from django.apps import apps
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListCreateAPIView
from drf_spectacular.utils import extend_schema
from bookings.serializers import AppointmentCancellationSerializer, AppointmentCreateSerialier, AppointmentRescheduleSerializer, AppointmentsSerializer
from bookings.services import BookingService
from utils.permissions import PublicUserPermissionsOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Case, When, Value, IntegerField, Q
from django.utils import timezone


class AppointmentsView(ListCreateAPIView, GenericViewSet):
    model = apps.get_model('bookings', 'AppointmentsModel')
    serializer_class = AppointmentsSerializer
    queryset = model.objects.all()
    search_fields = ['start_time', ]

    class_path = 'appointments'


    def get_queryset(self):
        now = timezone.now()
        qs = self.queryset.annotate(
                sort_priority=Case(
                    When(
                        Q(start_time__gte=now) &
                        Q(status__in=["PENDING", "ONGOING"]),
                        then=Value(0),
                    ),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by("sort_priority", "start_time")
        
        # all if admin
        if self.request.user.user_type == 'public': # type: ignore
            qs = qs.filter(patient=self.request.user)
        elif self.request.user.user_type == 'doctor': # type: ignore
            qs = qs.filter(doctor=self.request.user)
        return qs

    def get_permissions(self):
        """
        Everything else uses the default (AuthenticatedUserPermission).
        """
        if self.action in ('create', 'cancel', ):
            return [PublicUserPermissionsOnly()]
        return super().get_permissions()


    @extend_schema(
        request=AppointmentCreateSerialier,
        tags=["bookings"],                               
    )
    def create(self, request, *args, **kwargs):
        self.serializer_class = AppointmentCreateSerialier
        return super().create(request, *args, **kwargs)


    @extend_schema(
        request=AppointmentCancellationSerializer,
        tags=["bookings"],                               
        )
    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk):
        BookingService().cancel_appointment(request, pk)
        return Response({'detail': "Cancellation has been successful"})


    @extend_schema(
        request=AppointmentRescheduleSerializer,
        tags=["bookings"],                               
        )
    @action(detail=True, methods=['patch'], url_path='reschedule')
    def reschedule(self, request, pk):
        BookingService().reschedule_appointment(request, pk)
        return Response({'details': "Appointment has been rescheduled successful"})

    

    
                
