import re
from unicodedata import category
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from SmartMove.models import Category, Exercise
from SmartMove.serializers import ExerciseSerializer, CategorySerializer
from django.core.exceptions import ObjectDoesNotExist
    
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from SmartMove.models import Trainee, Coach
from SmartMove.serializers import UserSerializer, TraineeSerializer, CoachSerializer

from django.core.exceptions import ObjectDoesNotExist

all_tokens = {}


def get_tokens_for_user(user):
    global all_tokens

    username = user.username
    if username in all_tokens and all_tokens[username] is not None:
        return all_tokens[username]

    token = str(AccessToken.for_user(user))

    all_tokens[username] = token
    return token


"""
def token_is_valid(request):

    if "Authorization" not in request.headers or len(request.headers["Authorization"].split()) != 2:
        return Response({
            "Message": "Please provide a valid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get user
    username = request.data['username']
    user = User.objects.get(username=username)

    if not user:
        return Response({
            "Message": "User doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get provided token
    provided_token = request.headers['Authorization'].split(' ')[1]

    # Get token
    token = get_tokens_for_user(user)

    if token != provided_token:
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "Message": "Token is valid",
        "Code": "HTTP_200_OK",
    }, status=status.HTTP_200_OK)
"""


def token_is_valid(request):
    # Check headers
    if "Authorization" not in request.headers or len(request.headers["Authorization"].split()) != 2:
        return False

    # Get user
    username = request.data['username']
    user = User.objects.get(username=username)
    if not user:
        return False

    # Get provided token
    provided_token = request.headers['Authorization'].split(' ')[1]

    # Get token
    token = get_tokens_for_user(user)
    if token != provided_token:
        return False

    return True


@api_view(['POST'])
def register(request):

    if "email" not in request.data or "username" not in request.data \
            or "password" not in request.data or "account_type" not in request.data:
        return Response({
            "Message": "Please provide all required fields",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    email = request.data['email']
    username = request.data['username']
    password = request.data['password']
    account_type = request.data['account_type']

    # Authenticate user
    user = authenticate(username=username, password=password)

    if not user:

        # Save user
        user = User.objects.create_user(username, email, password)
        user.save()

        if account_type == "Trainee":
            trainee = Trainee.objects.create(user=user)
            trainee.save()

        elif account_type == "Coach":
            coach = Coach.objects.create(user=user)
            coach.save()

        token = get_tokens_for_user(user)

        return Response({
            "Message": "Register Successful",
            "Code": "HTTP_200_OK",
            "Authorization": "Token " + token
        }, status=status.HTTP_200_OK)

    return Response({
        "Message": "User already exists",
        "Code": "HTTP_400_BAD_REQUEST",
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def login(request):
    username = request.data['username']
    password = request.data['password']

    user = authenticate(request, username=username, password=password)

    if user:
        # Get token
        token = get_tokens_for_user(user)

        return Response({
            "Message": "Login Successful",
            "Code": "HTTP_200_OK",
            "Authorization": "Token " + token
        }, status=status.HTTP_200_OK)

    return Response({
        "Message": "User doesn't exist",
        "Code": "HTTP_400_BAD_REQUEST",
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    if not token_is_valid(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = request.data['username']
    all_tokens[username] = None

    return Response({
        "Message": "Logout Successful",
        "Code": "HTTP_200_OK",
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def profile(request):
    if not token_is_valid(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get username
    username = request.data['username']

    user = User.objects.get(username=username)
    if not user:
        return Response({
            "Message": "User doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "Message": "Profile Obtained",
        "Content": UserSerializer(user).data,
        "Code": "HTTP_200_OK",
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def trainee_profile(request):
    if not token_is_valid(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get username
    username = request.data['username']

    user = User.objects.get(username=username)
    if not user:
        return Response({
            "Message": "User doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        trainee = Trainee.objects.get(user=user)
    except ObjectDoesNotExist:
        return Response({
            "Message": "Coach doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    if not trainee:
        return Response({
            "Message": "Trainee doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "Message": "Trainee Profile Obtained",
        "Content": TraineeSerializer(trainee).data,
        "Code": "HTTP_200_OK",
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def coach_profile(request):
    if not token_is_valid(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get username
    username = request.data['username']

    user = User.objects.get(username=username)
    if not user:
        return Response({
            "Message": "User doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        coach = Coach.objects.get(user=user)
    except ObjectDoesNotExist:
        return Response({
            "Message": "Coach doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    if not coach:
        return Response({
            "Message": "Coach doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "Message": "Coach Profile Obtained",
        "Content": CoachSerializer(coach).data,
        "Code": "HTTP_200_OK",
    }, status=status.HTTP_200_OK)
    
    
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
