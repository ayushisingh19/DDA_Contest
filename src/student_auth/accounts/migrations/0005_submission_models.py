from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_delete_passwordresettoken"),
    ]

    operations = [
        migrations.CreateModel(
            name="Submission",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("code", models.TextField()),
                ("language", models.CharField(default="python", max_length=20)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("QUEUED", "QUEUED"),
                            ("RUNNING", "RUNNING"),
                            ("DONE", "DONE"),
                            ("ERROR", "ERROR"),
                        ],
                        default="QUEUED",
                        max_length=10,
                    ),
                ),
                ("score", models.FloatField(default=0)),
                ("max_score", models.FloatField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("judge0_tokens", models.JSONField(blank=True, default=list)),
                ("judge0_raw", models.JSONField(blank=True, default=dict)),
                (
                    "problem",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="accounts.problem",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="accounts.student",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SubmissionTestCaseResult",
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
                ("index", models.PositiveIntegerField()),
                ("group", models.CharField(default="default", max_length=50)),
                ("weight", models.FloatField(default=1.0)),
                ("stdin", models.TextField(blank=True, null=True)),
                ("expected_output", models.TextField(blank=True, null=True)),
                ("output", models.TextField(blank=True, null=True)),
                ("passed", models.BooleanField(default=False)),
                ("status", models.CharField(default="Pending", max_length=50)),
                ("time_ms", models.FloatField(default=0)),
                ("memory_kb", models.IntegerField(default=0)),
                ("judge0_raw", models.JSONField(blank=True, default=dict)),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="results",
                        to="accounts.submission",
                    ),
                ),
            ],
            options={
                "unique_together": {("submission", "index")},
            },
        ),
    ]
