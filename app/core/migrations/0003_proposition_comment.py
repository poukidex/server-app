# Generated by Django 4.1.2 on 2022-10-10 03:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_approbation_rename_created_by_index_creator_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposition",
            name="comment",
            field=models.CharField(default="Some comment", max_length=255),
            preserve_default=False,
        ),
    ]