

from rest_framework import serializers

from bookings.models import AppointmentsModel


class AppointmentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppointmentsModel
        fields = '__all__'



