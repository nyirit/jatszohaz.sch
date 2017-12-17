# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-16 19:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20171216_1114'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={'permissions': (('manage_inventory', 'Manage Inventory'),)},
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='inventory.GamePiece'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='missing_items',
            field=models.CharField(blank=True, max_length=100, verbose_name='Missing items'),
        ),
    ]
