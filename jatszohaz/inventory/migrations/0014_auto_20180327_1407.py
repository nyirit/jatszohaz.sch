# Generated by Django 2.0.1 on 2018-03-27 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_auto_20180327_1405'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gamegroup',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='gamepiece',
            options={'ordering': ['game_group__name']},
        ),
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={'ordering': ['created'], 'permissions': (('manage_inventory', 'Manage Inventory'),)},
        ),
    ]
