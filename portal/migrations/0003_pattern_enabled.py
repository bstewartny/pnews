# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-07-25 21:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_entity_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='pattern',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]
