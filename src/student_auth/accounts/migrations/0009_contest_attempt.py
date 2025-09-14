from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_usersolution_fastest_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContestAttempt",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("duration_minutes", models.PositiveIntegerField(default=60)),
                ("end_at", models.DateTimeField()),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("ended_reason", models.CharField(blank=True, max_length=20, null=True)),
                ("is_locked", models.BooleanField(default=False)),
                (
                    "contest",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="attempts", to="accounts.contest"),
                ),
                (
                    "student",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="accounts.student"),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="contestattempt",
            index=models.Index(fields=["student", "end_at"], name="accounts_co_student_0ee304_idx"),
        ),
    ]
