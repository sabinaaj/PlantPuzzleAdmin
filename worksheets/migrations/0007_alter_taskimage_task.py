# Generated by Django 5.0.9 on 2024-11-17 21:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worksheets', '0006_remove_task_image_alter_task_text_taskimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskimage',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='worksheets.task'),
        ),
    ]
