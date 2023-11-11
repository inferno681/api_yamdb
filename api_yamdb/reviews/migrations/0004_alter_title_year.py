# Generated by Django 3.2 on 2023-11-11 01:57

import api.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_alter_title_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.IntegerField(validators=[api.validators.validate_year]),
        ),
    ]
