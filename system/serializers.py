

from rest_framework import serializers

from system.models import DataChangesAndSuspectedActivity


class SystemErrorsLogsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataChangesAndSuspectedActivity
        fields = '__all__'



