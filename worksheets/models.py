from django.db import models
from django.db.models import Model


class TaskType(models.Model):
    type = models.CharField(max_length=100)


class Worksheet(models.Model):
    title = models.CharField(max_length=100)


class Task(models.Model):
    text = models.TextField(blank=True, null=True)
    type = models.ManyToManyField(TaskType)
    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE)


class Question(models.Model):
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)


class Option(models.Model):
    text = models.CharField()
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

