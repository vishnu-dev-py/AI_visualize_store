from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import UploadedScene, DetectedObject
from .serializers import UploadedSceneSerializer
from .detector import detect_objects
from products.models import Product
from products.serializers import ProductSerializer


@method_decorator(csrf_exempt, name='dispatch')
class SceneUploadView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        image = request.FILES.get("image")

        if not image:
            return Response({"error": "Image is required"}, status=400)

        scene = UploadedScene.objects.create(image=image)

        detections = detect_objects(scene.image.path)
        saved_objects = []

        for item in detections:
            obj = DetectedObject.objects.create(
                scene=scene,
                label=item["label"],
                x1=item["x1"],
                y1=item["y1"],
                x2=item["x2"],
                y2=item["y2"],
                confidence=item["confidence"]
            )

            saved_objects.append({
                "id": obj.id,
                "label": obj.label,
                "confidence": obj.confidence,
                "x1": obj.x1,
                "y1": obj.y1,
                "x2": obj.x2,
                "y2": obj.y2,
            })

        return Response({
            "scene_id": scene.id,
            "image": request.build_absolute_uri(scene.image.url),
            "detections": saved_objects
        }, status=201)


class SceneObjectsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, scene_id):
        try:
            scene = UploadedScene.objects.get(id=scene_id)
        except UploadedScene.DoesNotExist:
            return Response({"error": "Scene not found"}, status=404)

        serializer = UploadedSceneSerializer(scene, context={'request': request})
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class SuggestionView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, scene_id, object_id):
        try:
            obj = DetectedObject.objects.get(id=object_id, scene_id=scene_id)
        except DetectedObject.DoesNotExist:
            return Response({"error": "Object not found"}, status=404)

        products = Product.objects.filter(category__iexact=obj.label).order_by('-id')
        serializer = ProductSerializer(products, many=True, context={'request': request})

        return Response({
            "clicked_object": obj.label,
            "object_box": {
                "x1": obj.x1,
                "y1": obj.y1,
                "x2": obj.x2,
                "y2": obj.y2,
            },
            "products": serializer.data
        })