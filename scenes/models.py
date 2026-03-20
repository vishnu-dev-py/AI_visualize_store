from django.db import models


class UploadedScene(models.Model):
    image = models.ImageField(upload_to='scenes/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scene {self.id}"


class DetectedObject(models.Model):
    scene = models.ForeignKey(
        UploadedScene,
        on_delete=models.CASCADE,
        related_name='detected_objects'
    )
    label = models.CharField(max_length=100)
    x1 = models.FloatField(default=0)
    y1 = models.FloatField(default=0)
    x2 = models.FloatField(default=0)
    y2 = models.FloatField(default=0)
    confidence = models.FloatField(default=1.0)

    def __str__(self):
        return f"{self.label} - Scene {self.scene.id}"