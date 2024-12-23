# Generated by Django 5.0.6 on 2024-07-31 15:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Experiment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Results",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user_session_id",
                    models.CharField(default="no_session_id", max_length=2000),
                ),
                ("answers_formal", models.JSONField(default=dict)),
                ("answers_social", models.JSONField(default=dict)),
                ("answers_pheno", models.JSONField(default=dict)),
                ("answers_intuitive", models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_id", models.CharField(max_length=200)),
                ("session_id", models.CharField(default="no_id", max_length=40)),
                (
                    "experiment_group",
                    models.CharField(default="no_group_assigned", max_length=20),
                ),
                ("age", models.IntegerField(default=0)),
                (
                    "country",
                    models.CharField(default="no_group_assigned", max_length=20),
                ),
                ("competency", models.CharField(default="no_answer", max_length=7)),
                ("antibot", models.IntegerField(default=0)),
                ("complexity_formal", models.IntegerField(default=0)),
                ("complexity_social", models.IntegerField(default=0)),
                ("complexity_pheno", models.IntegerField(default=0)),
                ("complexity_intuitive", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="AnswersSocial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    models.CharField(
                        choices=[
                            ("urban city", "urban"),
                            ("rural, small town", "rural"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="myapp.experiment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AnswersPheno",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    models.CharField(
                        choices=[
                            ("Berlin", "Berlin"),
                            ("Los Angeles", "Los Angeles"),
                            ("New York", "New York"),
                            ("Paris", "Paris"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="myapp.experiment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AnswersIntuitive",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    models.CharField(
                        choices=[
                            ("high population density", "high"),
                            ("medium population density", "medium"),
                            ("low population density", "low"),
                            ("delegate to the AI", "AI"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="myapp.experiment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AnswersFormal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    models.CharField(
                        choices=[
                            ("high population density", "high"),
                            ("medium population density", "medium"),
                            ("low population density", "low"),
                            ("delegate to the AI", "AI"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="myapp.experiment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="")),
                ("name", models.CharField(max_length=200)),
                ("ai_answer", models.CharField(default="no_answer", max_length=12)),
                ("ai_predicted_correctly", models.BooleanField(default="False")),
                ("ai_delegate", models.BooleanField(default="False")),
                (
                    "correct_answer",
                    models.CharField(default="no_answer", max_length=12),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="myapp.experiment",
                    ),
                ),
            ],
        ),
    ]
