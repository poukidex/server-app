# Generated by Django 4.1.2 on 2022-10-29 08:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_publication_primary_color_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="publication",
            name="primary_color",
        ),
        migrations.RemoveField(
            model_name="publication",
            name="secondary_color",
        ),
        migrations.AddField(
            model_name="publication",
            name="dominant_colors",
            field=models.JSONField(blank=True, default={}, null=True),
        ),
    ]
