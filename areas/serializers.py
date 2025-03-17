from rest_framework import serializers

from worksheets.serializers import WorksheetSerializer
from .models import Area, Plant, PlantImage

class PlantImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PlantImage
        fields = ['id', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class PlantSerializer(serializers.ModelSerializer):
    images = PlantImageSerializer(many=True, read_only=True, source='plantimage_set')

    class Meta:
        model = Plant
        fields = ['id', 'name', 'images']


class AreaSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    worksheets = WorksheetSerializer(many=True, read_only=True, source='worksheet_set')
    plants = PlantSerializer(many=True, read_only=True, source='plant_set')

    class Meta:
        model = Area
        fields = ['id', 'title', 'icon_url', 'worksheets', 'plants']

    def get_icon_url(self, obj):
        request = self.context.get('request')
        if obj.icon:
            return request.build_absolute_uri(obj.icon.url)
        return None
