# Generated by Django 4.1.2 on 2022-10-07 11:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("userauth", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="picture",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Picture"
            ),
        ),
    ]
