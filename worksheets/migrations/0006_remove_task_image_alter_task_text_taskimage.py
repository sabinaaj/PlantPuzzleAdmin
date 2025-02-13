# Generated by Django 5.0.9 on 2024-11-17 21:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worksheets', '0005_remove_question_image_task_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='image',
        ),
        migrations.AlterField(
            model_name='task',
            name='text',
            field=models.TextField(),
        ),
        migrations.CreateModel(
            name='TaskImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='question_images/')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='worksheets.task')),
            ],
        ),
    ]
