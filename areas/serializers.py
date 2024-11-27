from rest_framework import serializers
from .models import Area

class AreaSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ['id', 'title', 'icon_url']

    def get_icon_url(self, obj):
        request = self.context.get('request')  # Získání požadavku z kontextu
        if obj.icon:
            return request.build_absolute_uri(obj.icon.url)
        return None
