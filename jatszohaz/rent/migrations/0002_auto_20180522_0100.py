# Generated by Django 2.0.1 on 2018-05-22 01:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rent',
            name='renter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rents', to=settings.AUTH_USER_MODEL, verbose_name='Renter'),
        ),
    ]
