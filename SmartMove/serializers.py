from django.contrib.auth.models import User
from rest_framework import serializers

from SmartMove.models import RealTimeReport, Trainee, Coach


class RealTimeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealTimeReport
        fields = ('id', 'correctness', 'progress', 'finished_repetition', 'first_half')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class TraineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainee
        fields = ('user', 'weight', 'height')


class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ('user')
