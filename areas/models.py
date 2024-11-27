from django.db import models
from django.core.files.storage import default_storage
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Area(models.Model):
    title = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='areas/', null=True, blank=True)

@receiver(post_delete, sender=Area)
def delete_task_image(sender, instance, **kwargs):

    if instance.image:
        image_path = instance.image.path
        if default_storage.exists(image_path):
            default_storage.delete(image_path)


class Plant(models.Model):
    name = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    @property
    def image(self):
        first_image = self.plantimage_set.first()
        return first_image.image.url if first_image else None


class PlantImage(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=f'plants/')

@receiver(post_delete, sender=PlantImage)
def delete_task_image(sender, instance, **kwargs):

    if instance.image:
        image_path = instance.image.path
        if default_storage.exists(image_path):
            default_storage.delete(image_path)
