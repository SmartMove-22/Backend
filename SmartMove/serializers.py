from django.contrib.auth.models import User
from rest_framework import serializers

from SmartMove.models import Trainee, Coach, Exercise, Report, RealTimeReport


class RealTimeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealTimeReport
        fields = ('id', 'correctness', 'progress', 'finished_repetition', 'first_half',
            'most_divergent_angle_landmark_first', 'most_divergent_angle_landmark_middle',
            'most_divergent_angle_landmark_last', 'most_divergent_angle_value')


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
        fields = 'user'


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ('id', 'coach', 'name', 'category', 'sets', 'reps', 'calories')


class AssignedExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ('id', 'coach', 'name', 'category', 'sets', 'reps', 'calories', 'completed', 'correctness', 'performance',
                  'improvement', 'calories_burned', 'grade')


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'trainee', 'exercises', 'date', 'completed', 'correctness', 'performance', 'improvement',
                  'calories_burned')
