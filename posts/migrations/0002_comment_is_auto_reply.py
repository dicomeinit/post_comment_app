# Generated by Django 5.1.2 on 2024-10-25 06:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="is_auto_reply",
            field=models.BooleanField(default=False),
        ),
    ]
