from os import environ
from django.apps import AppConfig

from .smart_move_analysis.reference_store import ReferenceStore
from .smart_move_analysis.knn import KNNRegressor
from .smart_move_analysis.utils import EXERCISE_ANGLES


class SmartmoveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SmartMove'
    
    reference_store = None
    knn_models = None

    def ready(self):
        self.reference_store = ReferenceStore(
            connection_string=f'mongodb://{environ.get("MONGO_USER", "username")}:{environ.get("MONGO_PASS", "password")}@mongodb'
        )

        self.knn_models = {}
        for exercise in self.reference_store.exercises():
            self.knn_models.update({exercise_half:KNNRegressor.from_exercise_references(
                    exercise_references=self.reference_store.get(*exercise_half),
                    exercise_angles=exercise if exercise in EXERCISE_ANGLES else None)
                for exercise_half in [
                    (exercise, True), (exercise, False)
                ]
            })
