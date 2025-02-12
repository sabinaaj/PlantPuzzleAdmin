from rest_framework import serializers

from worksheets.serializers import WorksheetSerializer
from .models import Area

class AreaSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    worksheets = WorksheetSerializer(many=True, read_only=True, source='worksheet_set')

    class Meta:
        model = Area
        fields = ['id', 'title', 'icon_url', 'worksheets']

    def get_icon_url(self, obj):
        request = self.context.get('request')
        if obj.icon:
            return request.build_absolute_uri(obj.icon.url)
        return None


