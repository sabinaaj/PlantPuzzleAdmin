from rest_framework import serializers
from .models import Worksheet

class WorksheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worksheet
        fields = ['id', 'title', 'area']