

from rest_framework import serializers

from hrm.models import DoctorsWorkScheduleModel


class WorkScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = DoctorsWorkScheduleModel
        fields = '__all__'


