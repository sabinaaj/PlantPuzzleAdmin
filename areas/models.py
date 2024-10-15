from django.db import models

class Area(models.Model):
    title = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='areas/', null=True, blank=True)


class Plant(models.Model):
    name = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)


class PlantImage(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=f'plants/{plant.name}')

