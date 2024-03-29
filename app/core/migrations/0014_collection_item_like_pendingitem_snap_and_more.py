# Generated by Django 4.1.7 on 2023-04-07 19:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0013_pendingpublication"),
    ]

    operations = [
        migrations.RenameField(
            model_name="Publication", old_name="index", new_name="collection"
        ),
        migrations.RenameField(
            model_name="Proposition", old_name="publication", new_name="item"
        ),
        migrations.RenameField(
            model_name="Approbation", old_name="proposition", new_name="snap"
        ),
        migrations.RenameField(
            model_name="PendingPublication", old_name="index", new_name="collection"
        ),
        migrations.RenameModel(old_name="Index", new_name="Collection"),
        migrations.RenameModel(old_name="Publication", new_name="Item"),
        migrations.RenameModel(old_name="Proposition", new_name="Snap"),
        migrations.RenameModel(old_name="Approbation", new_name="Like"),
        migrations.RenameModel(old_name="PendingPublication", new_name="PendingItem"),
    ]
