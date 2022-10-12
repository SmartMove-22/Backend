from django.shortcuts import render
from django.apps import apps
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from django.core.exceptions import ObjectDoesNotExist

from SmartMove.models import Trainee, Coach
from SmartMove.serializers import RealTimeReportSerializer, UserSerializer, TraineeSerializer, CoachSerializer
from .smart_move_analysis.reference_store import LandmarkData
from .smart_move_analysis.utils import landmark_list_angles


@api_view(['POST'])
def exercise_analysis(request):

    time = int(request.data['time'])
    repetition_half = int(request.data['repetition_half'])
    exercise_category = request.data['exercise_category']
    landmarks_coordinates = [request.data[str(i)] for i in range(33)]

    smartmoveConfig = apps.get_app_config('SmartMoveConfig')

    knn_model = smartmoveConfig.knn_models[(exercise_category, repetition_half == 1)]

    if knn_model:
        landmark_angles = landmark_list_angles([
            LandmarkData(visibility=None, **coordinates) for coordinates in landmarks_coordinates
        ])
        correctness, most_divergent_angle_value, most_divergent_angle_idx = knn_model.correctness(landmark_angles)
        progress = knn_model.progress(landmark_angles)
    else:
        # TODO: error response
        pass

    # TODO: repetitions aren't tracked yet (the value of 'repetition')
    repetition = 0
    if progress > 0.95:
        repetition_half = 1 if repetition_half == 2 else 2
        if repetition_half == 1:
            repetition = 1

    # Convert to Python data types that can then be easily rendered into JSON (Example)
    response = RealTimeReportSerializer(correctness=correctness, progress=progress, repetition=repetition, repetition_half=repetition_half)

    return Response(response, status=status.HTTP_200_OK)

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
