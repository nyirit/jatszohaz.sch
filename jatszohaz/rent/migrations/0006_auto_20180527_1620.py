# Generated by Django 2.0.1 on 2018-05-27 16:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0005_auto_20180527_1615'),
    ]

    operations = [
        migrations.RenameField(
            model_name='renthistory',
            old_name='new_game',
            new_name='added_game',
        ),
    ]
