# Generated by Django 2.0.1 on 2018-05-22 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0002_auto_20180522_0100'),
    ]

    operations = [
        migrations.AddField(
            model_name='renthistory',
            name='notes',
            field=models.CharField(max_length=300, null=True, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='renthistory',
            name='new_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('gaveout', 'Gave out'), ('inmyroom', 'In my room'), ('back', 'Brought back'), ('declined', 'Declined'), ('cancelled', 'Cancelled')], max_length=20, null=True, verbose_name='Status'),
        ),
    ]
