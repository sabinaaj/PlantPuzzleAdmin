# Generated by Django 5.0.9 on 2024-10-15 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitors', '0002_alter_schoolgroup_group'),
    ]

    operations = [
        migrations.RenameField(
            model_name='school',
            old_name='school_group',
            new_name='school_groups',
        ),
        migrations.AlterField(
            model_name='achievement',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
