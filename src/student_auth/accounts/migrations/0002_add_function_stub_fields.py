# Generated manually for add_function_stub_fields

from django.db import migrations, models
from django.db.models import JSONField


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),  # Adjust this to the latest migration number
    ]

    operations = [
        migrations.AddField(
            model_name="problem",
            name="function_name",
            field=models.CharField(
                blank=True,
                help_text="Function name for starter code generation (e.g., 'add_numbers')",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="problem",
            name="function_params",
            field=JSONField(
                blank=True,
                default=list,
                help_text="List of parameter names (e.g., ['a', 'b'])",
            ),
        ),
        migrations.AddField(
            model_name="problem",
            name="return_type",
            field=models.CharField(
                blank=True,
                help_text="Return type hint (e.g., 'int', 'List[int]')",
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="problem",
            name="default_stub",
            field=JSONField(
                blank=True,
                default=dict,
                help_text="Custom starter code by language (e.g., {'python': 'def solution():', 'java': 'public class Solution {}'})",
            ),
        ),
    ]
