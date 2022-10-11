from rest_framework import serializers
from SmartMove.models import RealTimeReport


class RealTimeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealTimeReport
        fields = ('id', 'correctness', 'progress', 'repetition', 'repetition_half')