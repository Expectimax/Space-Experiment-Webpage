# Generated by Django 5.0.6 on 2024-08-05 21:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0009_feedbackresults"),
    ]

    operations = [
        migrations.AddField(
            model_name="visitors",
            name="formal_images",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="visitors",
            name="intuitive_images",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="visitors",
            name="pheno_images",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="visitors",
            name="social_images",
            field=models.JSONField(default=dict),
        ),
    ]