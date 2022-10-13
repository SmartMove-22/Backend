from django.contrib.auth.models import User
from SmartMove.models import Exercise, Category,  Trainee, Coach
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ('coach_username','name', 'category', 'sets','reps','calories')
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category', 'sub_category')

class TraineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainee
        fields = ('user', 'weight', 'height')


class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ('user')
