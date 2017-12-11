# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-11 12:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20171210_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rent',
            name='renter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rents', to=settings.AUTH_USER_MODEL),
        ),
    ]
