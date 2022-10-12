from django.shortcuts import render
from rest_framework import status
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from rest_framework.response import Response

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

from rest_framework_simplejwt.tokens import RefreshToken

from SmartMove.serializers import UserSerializer


def get_tokens_for_user(user):

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def token_is_valid(provided_token, username):

    # Get username
    user = User.objects.get(username=username)
    if not user:
        return Response({
            "Message": "User doesn't exist",
            "Code": "HTTP_400_BAD_REQUEST",
        }, status=status.HTTP_400_BAD_REQUEST)

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


@api_view(['POST'])
@permission_classes((AllowAny,))
def register(request):

    email = request.data['email']
    username = request.data['username']
    password = request.data['password']

    # Authenticate user
    user = authenticate(username=username, password=password)

    if not user:

        # Save user
        user = User.objects.create_user(username, email, password)
        user.save()

        # Get token
        token = get_tokens_for_user(user)

        return Response({
            "Message": "Register Successful",
            "Code": "HTTP_200_OK",
            "Authorization": "Token " + token['access']
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
            "Authorization": "Token " + token['access']
        }, status=status.HTTP_200_OK)

    return Response({
        "Message": "User doesn't exist",
        "Code": "HTTP_400_BAD_REQUEST",
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):

    # If needed later, blacklist token
    return Response(status=status.HTTP_200_OK)
