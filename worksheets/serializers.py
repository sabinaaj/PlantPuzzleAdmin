from rest_framework import serializers
from .models import Worksheet, Task, Question, Option, TaskImage, TaskType

from random import shuffle


class WorksheetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worksheet
        fields = ['id', 'title', 'area']


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True, source='option_set')

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        task = instance.task

        if task and task.type == TaskType.objects.get(type=TaskType.Type.MULTIPLE_CHOICES_PICTURE):
            options = representation['options']
            new_options = []

            for option in representation['options']:
                if option['is_correct']:
                    new_options.append(option)
                    options.remove(option)

            shuffle(options)
            new_options.extend(options[:3])
            shuffle(new_options)

            representation['options'] = new_options

        if task and task.type == TaskType.objects.get(type=TaskType.Type.PAIRS):
            shuffle(representation['options'])

        return representation


class TaskImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = TaskImage
        fields = ['id', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class TaskSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True, source='question_set')
    images = TaskImageSerializer(many=True, read_only=True, source='taskimage_set')

    class Meta:
        model = Task
        fields = ['id', 'text', 'type', 'questions', 'images']

class WorksheetSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True, source='task_set')

    class Meta:
        model = Worksheet
        fields = ['id', 'title', 'tasks']