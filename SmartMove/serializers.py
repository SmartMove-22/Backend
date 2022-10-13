from django.contrib.auth.models import User
from rest_framework import serializers

from SmartMove.models import Trainee, Coach, Exercise, Report, AssignedExercise, Category


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


class ExerciseSerializer(serializers.ModelSerializer):
    coach = CoachSerializer(many=False, read_only=True)

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
        fields = ('id', 'trainee', 'exercises', 'date', 'completed', 'correctness', 'performance', 'improvement',
                  'calories_burned')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category', 'sub_category')