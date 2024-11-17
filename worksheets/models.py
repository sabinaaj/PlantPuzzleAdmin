from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage


class TaskType(models.Model):
    class Type(models.IntegerChoices):
        TWO_CHOICES = 1, 'Vyber ze 2 možností'
        CHOICES = 2, 'Vyber správnou možnost'
        CHOICES_PICTURE = 3, 'Vyber správnou možnost s obrázkem'
        MULTIPLE_CHOICES_PICTURE = 4, 'Obrázek s čísly'
        PAIRS = 5, 'Spoj dvojice'

    type = models.IntegerField(choices=Type.choices, default=Type.TWO_CHOICES)


class Worksheet(models.Model):
    from visitors.models import SchoolGroup
    from areas.models import Area

    title = models.CharField(max_length=100)
    school_groups = models.ManyToManyField(SchoolGroup)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)


class Task(models.Model):
    text = models.TextField()
    type = models.ForeignKey(TaskType, on_delete=models.DO_NOTHING, blank=True, null=True)
    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE)


class Question(models.Model):
    text = models.TextField(blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)


class Option(models.Model):
    text = models.CharField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class TaskImage(models.Model):
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, blank=True, null=True)
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
