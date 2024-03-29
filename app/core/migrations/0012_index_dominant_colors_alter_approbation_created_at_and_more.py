# Generated by Django 4.1.7 on 2023-04-04 11:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_index_object_name_alter_publication_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="index",
            name="dominant_colors",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="approbation",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="index",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="index",
            name="name",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="proposition",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="publication",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="publication",
            name="name",
            field=models.CharField(max_length=255),
        ),
    ]
