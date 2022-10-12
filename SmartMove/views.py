from django.shortcuts import render
from django.apps import apps
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from SmartMove.serializers import RealTimeReportSerializer
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

