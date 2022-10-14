from django.contrib.auth.models import User
from rest_framework import serializers

from SmartMove.models import Trainee, Coach, AssignedExercise, Exercise, Report, Category, RealTimeReport


class RealTimeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealTimeReport
        fields = ('id', 'correctness', 'progress', 'finished_repetition', 'first_half',
            'most_divergent_angle_landmark_first', 'most_divergent_angle_landmark_middle',
            'most_divergent_angle_landmark_last', 'most_divergent_angle_value')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class TraineeSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Trainee
        fields = ('user', 'trainee_coach', 'weight', 'height')


class CoachSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Coach
        fields = ['user']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category', 'sub_category')


class ExerciseSerializer(serializers.ModelSerializer):
    coach = CoachSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)

    class Meta:
        model = Exercise
        fields = ('id', 'coach', 'name', 'category', 'sets', 'reps', 'calories')


class AssignedExerciseSerializer(serializers.ModelSerializer):
    trainee = TraineeSerializer(many=False, read_only=True)
    exercise = ExerciseSerializer(many=False, read_only=True)

    class Meta:
        model = AssignedExercise
        fields = ('exercise', 'assigned_id', 'trainee', 'completed', 'correctness', 'performance', 'improvement', 'calories_burned', 'pacing', 'bpms', 'grade')


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'trainee', 'exercises', 'date', 'correctness', 'performance', 'improvement',
                  'calories_burned')
