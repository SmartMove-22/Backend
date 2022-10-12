from django.apps import AppConfig

from .smart_move_analysis.reference_store import ReferenceStore
from .smart_move_analysis.knn import KNNRegressor


class SmartmoveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SmartMove'
    
    # TODO: hardcoded
    mongodb_connection_string = 'mongodb://mongo:mongo@mongodb'
    reference_store = None
    knn_models = None

    def ready(self):
        self.reference_store = ReferenceStore(self.mongodb_connection_string)

        self.knn_models = {exercise_half:KNNRegressor.from_exercise_references(self.reference_store.get(*exercise_half))
            for exercise_half in [
                ('squat', True), ('squat', False),
                ('sit-up', True), ('sit-up', False),
                ('pushup', True), ('pushup', False)
            ]
        }
