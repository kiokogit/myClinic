from django.apps import apps
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from bookings.serializers import AppointmentCreateSerialier, AppointmentsSerializer
from utils.permissions import PublicUserPermissionsOnly


class AppointmentsView(ModelViewSet):
    model = apps.get_model('bookings', 'AppointmentsModel')
    serializer_class = AppointmentsSerializer
    queryset = model.objects.all()
    search_fields = ['start_time', ]

    class_path = 'appointments'


    def get_queryset(self):
        qs = self.queryset
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
        if self.action in ('create',):
            return [PublicUserPermissionsOnly()]
        return super().get_permissions()


    @extend_schema(
        request=AppointmentCreateSerialier,
        tags=["bookings"],                               
    )
    def create(self, request, *args, **kwargs):
        self.serializer_class = AppointmentCreateSerialier
        return super().create(request, *args, **kwargs)

    
                
