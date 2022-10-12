from django.shortcuts import render
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from SmartMove.serializers import UserSerializer


@api_view(['POST'])
def register(request):

    email = request.data['email']
    username = request.data['username']
    password = request.data['password']

    # Authenticate user
    user = authenticate(username=username, password=password)

    if not user:

        # request.session['username'] = username

        # Save user
        user = User.objects.create_user(username, email, password)
        user.save()

        return Response(status=status.HTTP_200_OK)

    return Response({'Message': 'User already exists.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def login(request):

    username = request.data['username']
    password = request.data['password']
    user = authenticate(request, username=username, password=password)

    if user:

        # Login user
        login(request, user)
        # request.session['username'] = username

        user = UserSerializer(user)
        return Response(user.data, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@login_required
@api_view(['POST'])
def logout(request):

    # del request.session['username']
    logout(request)

    return Response(status=status.HTTP_200_OK)
