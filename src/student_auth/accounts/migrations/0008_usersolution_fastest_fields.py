from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_merge_20250912_2041"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersolution",
            name="best_time_ms",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="usersolution",
            name="best_submission_id",
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
