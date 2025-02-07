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

class VisitorResponseSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    options = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(), many=True)

    class Meta:
        model = VisitorResponse
        fields = ['visitor', 'question', 'options', 'is_correct']

    def create(self, validated_data):
        options = validated_data.pop('options', [])
        visitor_response = VisitorResponse.objects.create(**validated_data)
        visitor_response.options.set(options)
        return visitor_response


class SuccessRateSerializer(serializers.ModelSerializer):
    worksheet = serializers.PrimaryKeyRelatedField(queryset=Worksheet.objects.all())

    class Meta:
        model = SuccessRate
        fields = ['rate', 'visitor', 'worksheet']
