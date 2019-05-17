# Generated by Django 2.2.1 on 2019-05-15 16:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0003_auto_20190506_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='max_allowed',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
