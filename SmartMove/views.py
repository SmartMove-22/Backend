from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from SmartMove.serializers import RealTimeReportSerializer


@api_view(['POST'])
def exercise_analysis(request):

    time = int(request.data['time'])
    repetition_half = int(request.data['repetition_half'])
    exercise_category = request.data['exercise_category']
    left_shoulder = request.data['LEFT_SHOULDER']
    right_shoulder = request.data['RIGHT_SHOULDER']

    # Convert to Python data types that can then be easily rendered into JSON (Example)
    response = RealTimeReportSerializer(correctness=0, progress=0, repetition=0, repetition_half=0)

    return Response(response, status=status.HTTP_200_OK)

