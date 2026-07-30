

from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import serializers, exceptions

from acl.models import CustomUser
from acl.serializers import UserListSerializer
from bookings.models import AppointmentRemarksModel, AppointmentsModel
from bookings.services import BookingService
from utils.exceptions import UserInputValidationError


class RemarksSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppointmentRemarksModel
        fields = [
            "date_created",
            "remark_for",
            "remark"
        ]

class AppointmentsSerializer(serializers.ModelSerializer):
    remarks = RemarksSerializer(many=True)
    status = serializers.SerializerMethodField(read_only=True)
    patient = UserListSerializer()
    doctor = UserListSerializer()

    class Meta:
        model = AppointmentsModel
        fields = [
            'id',
            "date_created",
            "status",
            "patient",
            "doctor",
            "start_time",
            "duration_in_minutes",
            "remarks"
        ]

    def get_status(self, obj):
        if obj.status == 'PENDING' and obj.start_time < datetime.now():
            return 'EXPIRED'
        return obj.status


class AppointmentCreateSerialier(serializers.Serializer):
    doctor = serializers.CharField()
    start_time = serializers.DateTimeField()
    remarks = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        if attrs['start_time'] < timezone.now() + timedelta(minutes=30):
            raise UserInputValidationError("Appointment booking time must be in the future")
        
        doctor = CustomUser.objects.filter(id=attrs.pop('doctor'), user_type='doctor').first()

        if not doctor:
            raise UserInputValidationError('Invalid appointment details. Please choose a doctor first.')
        
        # validate slot available
        if not BookingService().check_slot_is_available(doctor.id, str(attrs['start_time'])):
            raise UserInputValidationError("Time slot is not available for booking. Kindly try another time")

        attrs['patient'] = self.context['request'].user
        attrs['doctor'] = doctor

        return attrs

    def create(self, validated_data):
        rmk = None
        if validated_data.get('remarks'):
            rmk = validated_data.pop('remarks')
        instance = AppointmentsModel.objects.create(
            **validated_data
        )
        if rmk:
            instance.remarks.create(  # type:ignore
                remark=rmk,
                remark_for="APPOINTMENT_BOOKING"
            )
        return instance


class AppointmentRescheduleSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    remarks = serializers.CharField()


class AppointmentCancellationSerializer(serializers.Serializer):
    remarks = serializers.CharField()



