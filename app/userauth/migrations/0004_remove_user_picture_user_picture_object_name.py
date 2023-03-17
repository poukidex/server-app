# Generated by Django 4.1.7 on 2023-03-15 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0003_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='picture',
        ),
        migrations.AddField(
            model_name='user',
            name='picture_object_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Picture object name'),
        ),
    ]
