from django.urls import path
from .views import SceneUploadView, SceneObjectsView, SuggestionView

urlpatterns = [
    path('upload/', SceneUploadView.as_view(), name='scene-upload'),
    path('<int:scene_id>/objects/', SceneObjectsView.as_view(), name='scene-objects'),
    path('<int:scene_id>/suggestions/<int:object_id>/', SuggestionView.as_view(), name='scene-suggestions'),
]