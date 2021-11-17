# Generated by Django 2.2.24 on 2021-11-17 20:34

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_auto_20180315_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='image',
            field=django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format=None, keep_meta=True, null=True, quality=100, size=[500, 500], upload_to='', verbose_name='Image'),
        ),
    ]
