from django.db import models
from django.db.models import Model

from worksheets.models import Worksheet, Question, Option


class SchoolGroup(models.Model):
    class Group(models.IntegerChoices):
        MS = 1, 'Mateřská škola'
        ZS_1 = 2, 'První stupeň základní školy'
        ZS_2 = 3, 'Druhý stupeň základní školy / Nižší stupeň gymnázia'
        SS = 4, 'Střední škola / Vyšší stupeň gymnázia'

    group = models.IntegerField(choices=Group.choices, null=True, blank=True)


class School(models.Model):
    title = models.CharField(max_length=100)
    school_group = models.ManyToManyField(SchoolGroup)
    worksheets = models.ManyToManyField(Worksheet)


class Achievement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()


class Visitor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    school_group = models.ForeignKey(SchoolGroup, on_delete=models.CASCADE, null=True, blank=True)
    achievements = models.ManyToManyField(Achievement)


class VisitorResponse(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)


class SuccessRate(models.Model):
    rate = models.PositiveSmallIntegerField()
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE)
