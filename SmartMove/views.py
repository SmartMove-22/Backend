import re
from unicodedata import category
from django.shortcuts import render
from rest_framework import status
# from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from SmartMove.models import Category, Exercise
from SmartMove.serializers import ExerciseSerializer, CategorySerializer
from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required

# from SmartMove.serializers import RealTimeReportSerializer
# from SmartMove.serializers import UserSerializer


# Create your views here.

def create_category(data):
    
    try:    
        cat = Category.objects.get(category=data['category'], sub_category=data['sub_category'] )
        if not cat:
            cat = Category.objects.create(category=data['category'], sub_category=data['sub_category'] )
        
        return cat
    except ObjectDoesNotExist:
            cat = Category.objects.create(category=data['category'], sub_category=data['sub_category'] )
            return cat
    
                


@api_view(['POST', 'GET', 'DELETE'])
def manage_exercise(request):
   
    if request.method=='POST':
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
        except ObjectDoesNotExist:
            return Response({
                "Message": "Error creating Exercise",
                "Code": "HTTP_400_BAD_REQUEST",
            },status=status.HTTP_400_BAD_REQUEST)      
             
    if request.method=='GET':
        try:
            exer = Exercise.objects.all() 
            return Response({
                "Message": "Exercises Obtained",
                "Content": ExerciseSerializer(exer, many=True).data,
                "Code": "HTTP_200_OK",
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                "Message": "Exercise Table is Empty",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method=='DELETE':
        try:
            id_exer = request.data['id']

            # create a Exercise
            exe = Exercise.objects.get(id=id_exer)
            exe.delete()
            
            return Response({
                "Message": "Exercise Deleted",
                "Code": "HTTP_200_OK",
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                "Message": "Exercise Not Found",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_categories():
   
    try:
        cat = Category.objects.all() 
        return Response({
            "Message": "Exercises Obtained",
            "Content": ExerciseSerializer(cat, many=True).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({
            "Message": "Exercise Table is Empty",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST) 
             
   
@api_view(['GET'])
def exercises(request):
   
    name = request.data['name']

    # create a category
    category = request.data['category']['category']   
    sub_category = request.data['category']['sub_category']
    sets = request.data['sets']
    reps = request.data['reps']
    calories = request.data['calories']
    
    try:
        cat = Category.objects.all() 
        return Response({
            "Message": "Exercises Obtained",
            "Content": ExerciseSerializer(cat, many=True).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({
            "Message": "Exercise Table is Empty",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST) 
             

# def search_exercise(request):

#     name = request.data['name']
    
#     try:
#         exer = Exercise.objects.get(name=name) 
#         return Response({
#             "Message": "Exercise created",
#             "Content": ExerciseSerializer(exer, many=True).data,
#             "Code": "HTTP_200_OK",
#         }, status=status.HTTP_200_OK)
#     except ObjectDoesNotExist:
#         return Response({
#             "Message": " doesn't exist",
#             "Code": "HTTP_400_BAD_REQUEST",
#         }, status=status.HTTP_400_BAD_REQUEST)
    
