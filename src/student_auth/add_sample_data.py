# ruff: noqa: E402
import os
import json
from django.core.files.base import ContentFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
import django

django.setup()

from accounts.models import Contest, Problem, TestCase
from django.utils import timezone


def main():
    contest, _ = Contest.objects.get_or_create(
        name="Sample Contest",
        defaults={
            "start_at": timezone.now(),
            "duration_minutes": 120,
            "is_active": True,
        },
    )
    prob, _ = Problem.objects.get_or_create(
        contest=contest, code="P1", defaults={"title": "Sum A+B"}
    )

    # Create JSON testcases with groups and weights
    cases = {
        "test_cases": [
            {"stdin": "1 2\n", "expected_output": "3\n", "group": "basic", "weight": 1},
            {
                "stdin": "5 7\n",
                "expected_output": "12\n",
                "group": "basic",
                "weight": 1,
            },
            {
                "stdin": "100 200\n",
                "expected_output": "300\n",
                "group": "edge",
                "weight": 2,
            },
        ]
    }
    content = ContentFile(json.dumps(cases).encode("utf-8"), name="sample.json")
    for lang in ["python"]:
        tc, _ = TestCase.objects.get_or_create(problem=prob, language=lang)
        tc.file.save(f"{lang}_sum.json", content, save=True)
        tc.save()
    print("Seeded sample contest/problem/testcases.")


if __name__ == "__main__":
    main()
