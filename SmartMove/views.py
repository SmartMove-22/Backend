from django.shortcuts import render
from rest_framework import status
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from SmartMove.models import Trainee, Coach
from SmartMove.serializers import UserSerializer, TraineeSerializer, CoachSerializer, ExerciseSerializer

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


def check_token(request):

    if not token_is_valid(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)


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

    check_token(request)

    username = request.data['username']
    all_tokens[username] = None

    return Response({
        "Message": "Logout Successful",
        "Code": "HTTP_200_OK",
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def profile(request):

    check_token(request)

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

    check_token(request)

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

    check_token(request)

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


def is_trainee(user):

    try:
        # Check if trainee
        Trainee.objects.get(user=user)
        return True

    except ObjectDoesNotExist:
        return False


def is_coach(user):

        try:
            # Check if coach
            Coach.objects.get(user=user)
            return True

        except ObjectDoesNotExist:
            return False


def obtain_user_type(username):

    try:
        user = User.objects.get(username=username)

    except ObjectDoesNotExist:
        return None

    if is_trainee(user):
        return "TRAINEE"
    if is_coach(user):
        return "COACH"

    return None


@api_view(['GET'])
def user_type(request):

    check_token(request)

    # Get username
    username = request.data['username']
    account_type = obtain_user_type(username)

    if account_type:
        return Response({
            "Message": "User Type Obtained",
            "Content": {"userType": account_type},
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    return Response({
        "Message": "User doesn't exist",
        "Code": "HTTP_400_BAD_REQUEST",
    }, status=status.HTTP_400_BAD_REQUEST)


# --- Trainee Endpoints


@api_view(['GET', 'PUT', 'DELETE'])
def trainee_coach(request):

    check_token(request)

    if "username" not in request.data or "coach_username" not in request.data:
        return Response({
            "Message": "Missing username (trainee or coach)",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = request.data['username']

    # Check if trainee
    if obtain_user_type(username) != "TRAINEE":
        return Response({
            "Message": "User is not a trainee",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':

        user = User.objects.get(username=username)
        trainee = Trainee.objects.get(user=user)
        coach = trainee.trainee_coach

        if not coach:
            return Response({
                "Message": "No Coach",
                "Code": "HTTP_200_OK",
            }, status=status.HTTP_200_OK)

        return Response({
            "Message": "Coach Obtained",
            "Content": CoachSerializer(coach).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':

        coach_username = request.data['coach_username']

        # Check if coach
        if obtain_user_type(coach_username) != "COACH":
            return Response({
                "Message": "User is not a coach",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

        trainee = Trainee.objects.get(user=User.objects.get(username=username))
        if trainee.trainee_coach:
            return Response({
                "Message": "Trainee already has a coach",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

        coach = Coach.objects.get(user=User.objects.get(username=coach_username))

        trainee.trainee_coach = coach
        trainee.save()

        return Response({
            "Message": "Coach Added Successfully",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':

        user = User.objects.get(username=username)
        trainee = Trainee.objects.get(user=user)
        coach = trainee.trainee_coach

        if not coach:
            return Response({
                "Message": "No Coach",
                "Code": "HTTP_200_OK",
            }, status=status.HTTP_200_OK)

        trainee.trainee_coach = None
        trainee.save()

        return Response({
            "Message": "Coach Removed Successfully",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def assigned_exercises(request):

    check_token(request)

    if "username" not in request.data or "coach_username" not in request.data:
        return Response({
            "Message": "Missing username (trainee or coach)",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = request.data['username']

    # Check if trainee
    if obtain_user_type(username) != "TRAINEE":
        return Response({
            "Message": "User is not a trainee",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        trainee = Trainee.objects.get(user=user)
        exercises = trainee.assigned_exercises

        return Response({
            "Message": "Exercises Obtained",
            "Content": ExerciseSerializer(exercises, many=True).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({
            "Message": "No exercises",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def exercises_report(request):
    pass


# --- Coach Endpoints

