# Generated by Django 5.0.6 on 2024-08-02 16:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0004_alter_user_competency_alter_user_expectation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="country",
            field=models.CharField(default="no_country_assigned", max_length=20),
        ),
    ]
