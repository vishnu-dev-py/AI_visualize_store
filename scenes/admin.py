from django.contrib import admin
from .models import UploadedScene, DetectedObject

admin.site.register(UploadedScene)
admin.site.register(DetectedObject)
