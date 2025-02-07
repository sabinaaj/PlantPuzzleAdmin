from django.db import models

class SchoolGroup(models.Model):
    class Group(models.IntegerChoices):
        MS = 1, 'Mateřská škola'
        ZS_1 = 2, 'První stupeň základní školy'
        ZS_2 = 3, 'Druhý stupeň základní školy / Nižší stupeň gymnázia'
        SS = 4, 'Střední škola / Vyšší stupeň gymnázia'

    group = models.IntegerField(choices=Group.choices, default=Group.ZS_1)


class Achievement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)


class Visitor(models.Model):
    school_group = models.ManyToManyField(SchoolGroup)
    achievements = models.ManyToManyField(Achievement)


class VisitorResponse(models.Model):
    from worksheets.models import Question, Option

    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    options = models.ManyToManyField(Option)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class SuccessRate(models.Model):
    from worksheets.models import Worksheet

    rate = models.PositiveSmallIntegerField()
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
