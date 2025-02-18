from rest_framework import serializers
from .models import Visitor, SchoolGroup, VisitorResponse, SuccessRate
from worksheets.models import Question, Option, Worksheet


class VisitorSerializer(serializers.ModelSerializer):
    school_group = serializers.PrimaryKeyRelatedField(
        queryset=SchoolGroup.objects.all(),
        many=True
    )

    class Meta:
        model = Visitor
        fields = ['id', 'school_group']

class SchoolGroupSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source='get_group_display', read_only=True)

    class Meta:
        model = SchoolGroup
        fields = ['id', 'group']
