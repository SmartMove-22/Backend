from django.contrib.auth.models import User
from rest_framework import serializers

from SmartMove.models import Trainee, Coach, Exercise


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class TraineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainee
        fields = ('user', 'trainee_coach', 'assigned_exercises', 'weight', 'height')


class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ('user', 'coach_exercises')


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ('name', 'category', 'sets', 'reps', 'calories')