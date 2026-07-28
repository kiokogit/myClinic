

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers, exceptions

from acl.models import CustomUser
from bookings.models import AppointmentsModel
from bookings.services import BookingService


class AppointmentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppointmentsModel
        fields = [
            'id',
            "date_created",
            "status",
            "patient",
            "doctor",
            "start_time",
            "duration_in_minutes"
        ]


class AppointmentCreateSerialier(serializers.Serializer):
    doctor = serializers.CharField()
    start_time = serializers.DateTimeField()
    public_remarks = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        if attrs['start_time'] < timezone.now() + timedelta(minutes=30):
            raise exceptions.ValidationError("Appointment booking time must be in the future")
        
        doctor = CustomUser.objects.filter(id=attrs.pop('doctor'), user_type='doctor').first()

        if not doctor:
            raise serializers.ValidationError('Invalid appointment details. Please choose a doctor first.')
        
        # validate slot available
        if not BookingService().check_slot_is_available(doctor.id, str(attrs['start_time'])):
            raise exceptions.ValidationError("Time slot is not available for booking. Kindly try another time")

        attrs['patient'] = self.context['request'].user
        attrs['doctor'] = doctor

        return attrs

    def create(self, validated_data):
        instance = AppointmentsModel.objects.create(
            **validated_data
        )
        return instance


