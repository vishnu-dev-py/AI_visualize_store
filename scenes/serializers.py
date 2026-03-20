from rest_framework import serializers
from .models import UploadedScene, DetectedObject


class DetectedObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectedObject
        fields = '__all__'


class UploadedSceneSerializer(serializers.ModelSerializer):
    detected_objects = DetectedObjectSerializer(many=True, read_only=True)

    class Meta:
        model = UploadedScene
        fields = ['id', 'image', 'created_at', 'detected_objects']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if instance.image:
            if request:
                data['image'] = request.build_absolute_uri(instance.image.url)
            else:
                data['image'] = instance.image.url
        else:
            data['image'] = None

        return data