# Generated by Django 5.0.6 on 2024-08-13 13:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0021_completioncode"),
    ]

    operations = [
        migrations.AddField(
            model_name="completioncode",
            name="assigned",
            field=models.BooleanField(default=False),
        ),
    ]
