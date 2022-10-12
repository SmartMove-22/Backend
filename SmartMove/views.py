from pprint import pprint
import re
from unicodedata import category
from django.shortcuts import render
from rest_framework import status
# from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from SmartMove.models import Category, Exercise
from SmartMove.serializers import ExerciseSerializer, CategorySerializer

# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required

# from SmartMove.serializers import RealTimeReportSerializer
# from SmartMove.serializers import UserSerializer


# Create your views here.

def create_category(data):
    
    cat = Category.objects.create(category=data['category'], sub_category=data['sub_category'] )
    print(cat)
    
    return cat

@api_view(['POST'])
def create_exercise(request):
    print(request.user)
   
    try: 
        name = request.data['name']
        
        # create a category
        category = create_category(request.data['category'])
        sets = request.data['sets']
        reps = request.data['reps']
        calories = request.data['calories']
        
        # create a Exercise
        exe = Exercise.objects.create(name=name, category=category, sets=sets, reps=reps, calories=calories)
        
        return Response({
            "Message": "Exercise created",
            "Content": ExerciseSerializer(exe).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            "Message": "Error creating Exercise",
            "Code": "HTTP_400_BAD_REQUEST",
        },status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def search_exercise(request):

    lst_exercise = []
    name = request.data['name']
    
    try:
        exer = Exercise.objects.get(name=name) 
    except :
        return Response({
            "Message": "Coach doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)
   
    for e in exer:
        lst_exercise.append(e)    
    
    return Response({
            "Message": lst_exercise,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
def get_exercises(request):
     
    return Response({
            "Message": request.data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)
    
