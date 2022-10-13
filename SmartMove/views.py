from django.shortcuts import render
from rest_framework import status
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from SmartMove.models import Trainee, Coach, Report, Exercise, Category, AssignedExercise
from SmartMove.serializers import UserSerializer, TraineeSerializer, CoachSerializer, ExerciseSerializer, \
    ReportSerializer, AssignedExerciseSerializer, CategorySerializer

from django.core.exceptions import ObjectDoesNotExist

import datetime

all_tokens = {}


def get_username(request):
    token = request.headers['Authorization'].split(' ')[1]
    username = [key for key, value in all_tokens.items() if value == token]
    if len(username) == 0:
        return None

    return username[0]


def get_tokens_for_user(user):
    global all_tokens

    username = user.username
    if username in all_tokens and all_tokens[username] is not None:
        return all_tokens[username]

    token = str(AccessToken.for_user(user))

    all_tokens[username] = token
    return token


def check_token(request):

    # Check headers
    if "Authorization" not in request.headers or len(request.headers["Authorization"].split()) != 2:
        return False

    # Get user
    username = get_username(request)
    if not username:
        return False

    user = User.objects.get(username=username)
    if not user:
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
    global all_tokens

    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    all_tokens[username] = None

    return Response({
        "Message": "Logout Successful",
        "Code": "HTTP_200_OK",
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def profile(request):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

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
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

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
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    user = User.objects.get(username=username)
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
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

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

@api_view(['GET'])
def trainee_coaches(request):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    # Check if trainee
    if obtain_user_type(username) != "TRAINEE":
        return Response({
            "Message": "User is not a trainee",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Obtain coaches
        coaches = Coach.objects.all()

        return Response({
            "Message": "Coaches Obtained",
            "Content": CoachSerializer(coaches, many=True).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({
            "Message": "No coaches available",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def trainee_coach(request):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

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

        if "coach_username" not in request.data:
            return Response({
                "Message": "Missing coach username",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

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
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    # Check if trainee
    if obtain_user_type(username) != "TRAINEE":
        return Response({
            "Message": "User is not a trainee",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        trainee = Trainee.objects.get(user=user)
        exercises = AssignedExercise.objects.filter(trainee=trainee)

        return Response({
            "Message": "Exercises Obtained",
            "Content": AssignedExerciseSerializer(exercises, many=True).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({
            "Message": "No exercises",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def exercises_report(request):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    # Check if trainee
    if obtain_user_type(username) != "TRAINEE":
        return Response({
            "Message": "User is not a trainee",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get report
    try:
        user = User.objects.get(username=username)
        trainee = Trainee.objects.get(user=user)

        date = datetime.datetime.now()
        if "date" in request.data:
            date = request.data['date']

        reports = Report.objects.get(trainee=trainee, date=date)

        return Response({
            "Message": "Report Obtained for " + date,
            "Content": ReportSerializer(reports, many=True).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({
            "Message": "No reports",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def update_exercise(request):

    # pacing
    pass


@api_view(['PATCH'])
def trainee_weight(request):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    # Check if trainee
    if obtain_user_type(username) != "TRAINEE":
        return Response({
            "Message": "User is not a trainee",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    if "weight" not in request.data:
        return Response({
            "Message": "Missing weight",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    weight = request.data['weight']

    user = User.objects.get(username=username)
    trainee = Trainee.objects.get(user=user)
    trainee.weight = weight
    trainee.save()

    return Response({
        "Message": "Weight Updated Successfully",
        "Code": "HTTP_200_OK",
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def trainee_height(request):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    # Check if trainee
    if obtain_user_type(username) != "TRAINEE":
        return Response({
            "Message": "User is not a trainee",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    if "height" not in request.data:
        return Response({
            "Message": "Missing height",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    height = request.data['height']

    user = User.objects.get(username=username)
    trainee = Trainee.objects.get(user=user)
    trainee.height = height
    trainee.save()

    return Response({
        "Message": "Height Updated Successfully",
        "Code": "HTTP_200_OK",
    }, status=status.HTTP_200_OK)


# --- Coach Endpoints

@api_view(['GET'])
def coach_assigned_exercises(request):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    # Check if coach
    if obtain_user_type(username) != "COACH":
        return Response({
            "Message": "User is not a coach",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(username=username)
    coach = Coach.objects.get(user=user)

    try:
        exercises = Exercise.objects.filter(coach=coach)
        """
        all_assigned_exercises = []
        for exercise in exercises:
            all_assigned_exercises.append(
                AssignedExerciseSerializer(AssignedExercise.objects.filter(exercise=exercise), many=True).data)
        """
        all_assigned_exercises = AssignedExercise.objects.filter(exercise__in=exercises)

        return Response({
            "Message": "Assigned Exercises Obtained",
            "Content": AssignedExerciseSerializer(all_assigned_exercises, many=True).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({
            "Message": "No exercises",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def coach_assigned_exercises_trainee(request, traineeId):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    # Check if coach
    if obtain_user_type(username) != "COACH":
        return Response({
            "Message": "User is not a coach",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(username=username)
    coach = Coach.objects.get(user=user)

    try:
        trainee = Trainee.objects.get(user=User.objects.get(username=traineeId))
        exercises = AssignedExercise.objects.filter(trainee=trainee, exercise__coach=coach)

        return Response({
            "Message": "Exercises Obtained",
            "Content": AssignedExerciseSerializer(exercises, many=True).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({
            "Message": "No exercises",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
def coach_exercises(request):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    # Check if coach
    if obtain_user_type(username) != "COACH":
        return Response({
            "Message": "User is not a coach",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(username=username)
    coach = Coach.objects.get(user=user)

    if request.method == 'GET':

        try:
            # Obtain exercises
            exercises = Exercise.objects.filter(coach=coach)

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

    elif request.method == 'POST':

        if "name" not in request.data or "category" not in request.data or "sub_category" not in request.data \
                or "sets" not in request.data or "reps" not in request.data or "calories" not in request.data:
            return Response({
                "Message": "Please provide missing fields",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

        name = request.data['name']
        category = request.data['category']
        sub_category = request.data['sub_category']
        sets = request.data['sets']
        reps = request.data['reps']
        calories = request.data['calories']

        exercise_category = Category.objects.create(category=category, sub_category=sub_category)
        exercise = Exercise.objects.create(coach=coach, name=name, category=exercise_category,
                                           sets=sets, reps=reps, calories=calories)

        exercise.save()

        return Response({
            "Message": "Exercise Added Successfully",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':

        if "exercise_id" not in request.data:
            return Response({
                "Message": "Please provide the exercise",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

        exercise_id = request.data['exercise_id']

        try:
            exercise = Exercise.objects.get(id=exercise_id)
            exercise.delete()

            return Response({
                "Message": "Exercise Deleted Successfully",
                "Code": "HTTP_200_OK",
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({
                "Message": "Exercise does not exist",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
def coach_manage_exercise(request, traineeId, exerciseId):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    # Check if coach
    if obtain_user_type(username) != "COACH":
        return Response({
            "Message": "User is not a coach",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(username=username)
    coach = Coach.objects.get(user=user)

    try:
        trainee = Trainee.objects.get(user=User.objects.get(username=traineeId))
        if trainee.coach != coach:
            return Response({
                "Message": "Trainee is not assigned to you",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            exercise = Exercise.objects.get(id=exerciseId)

            if exercise.coach != coach:
                return Response({
                    "Message": "Exercise does not belong to coach",
                    "Code": "HTTP_400_BAD_REQUEST",
                }, status=status.HTTP_400_BAD_REQUEST)

            if request.method == 'POST':

                assigned_exercise = AssignedExercise.objects.get_or_create(exercise=exercise, trainee=trainee)[0]
                assigned_exercise.save()

                return Response({
                    "Message": "Exercise Assigned Successfully",
                    "Code": "HTTP_200_OK",
                }, status=status.HTTP_200_OK)

            elif request.method == 'DELETE':

                assigned_exercise = AssignedExercise.objects.get(exercise=exercise, trainee=trainee)
                assigned_exercise.delete()

                return Response({
                    "Message": "Exercise Unassigned Successfully",
                    "Code": "HTTP_200_OK",
                }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({
                "Message": "Exercise does not exist",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

    except ObjectDoesNotExist:
        return Response({
            "Message": "Trainee does not exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def evaluate_exercise(request, traineeId, exerciseId):
    check_token(request)
    if not check_token(request):
        return Response({
            "Message": "Invalid token",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

    username = get_username(request)

    user = User.objects.get(username=username)
    # Check if coach
    if obtain_user_type(username) != "COACH":
        return Response({
            "Message": "User is not a coach",
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

    try:

        try:
            trainee = Trainee.objects.get(user=User.objects.get(username=traineeId))
        except ObjectDoesNotExist:
            return Response({
                "Message": "Trainee does not exist",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            exercise = Exercise.objects.get(id=exerciseId, coach=coach)
            assigned_exercise = AssignedExercise.objects.get(exercise=exercise, trainee=trainee)
        except ObjectDoesNotExist:
            return Response({
                "Message": "Exercise does not exist",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

        if "grade" not in request.data:
            return Response({
                "Message": "Please provide the grade",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

        assigned_exercise.grade = request.data['grade']
        assigned_exercise.save()

        return Response({
            "Message": "Exercise Evaluated Successfully",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({
            "Message": "Assigned Exercise Not Found",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)


# --- Categories

@api_view(['GET'])
def exercise_category(request, category):
    try:
        cat = Category.objects.filter(category=category)
        return Response({
            "Message": "Categories Obtained",
            "Content": CategorySerializer(cat, many=True).data,
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({
            "Message": "No categories",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def exercises_categories(request):

    if request.method == 'GET':
        try:
            cat = Category.objects.all()
            return Response({
                "Message": "Categories Obtained",
                "Content": CategorySerializer(cat, many=True).data,
                "Code": "HTTP_200_OK",
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({
                "Message": "No categories",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':

        if "category" not in request.data or "sub_category" not in request.data:
            return Response({
                "Message": "Please provide the category and sub-category",
                "Code": "HTTP_400_BAD_REQUEST",
            }, status=status.HTTP_400_BAD_REQUEST)

        category = request.data['category']
        sub_category = request.data['sub_category']

        Category.objects.get_or_create(category=category, sub_category=sub_category)
        return Response({
            "Message": "Category Created",
            "Code": "HTTP_200_OK",
        }, status=status.HTTP_200_OK)
