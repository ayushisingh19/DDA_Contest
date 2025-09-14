# ruff: noqa: E402
import os
from django.core.files.base import ContentFile
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
import django

django.setup()

from accounts.models import Contest, Problem, TestCase


def main():
    contest, _ = Contest.objects.get_or_create(
        name="Practice Contest",
        defaults={
            "start_at": timezone.now(),
            "duration_minutes": 120,
            "is_active": True,
        },
    )

    problem_defaults = {
        "title": "Hello World",
        "description": "Return the classic 'Hello, World!' string.",
        "difficulty": "Easy",
        "constraints": "",
        "function_name": "hello_world",
        "function_params": [],
        "return_type": "str",
        "default_stub": {
            "python": 'def hello_world():\n    """Return the classic Hello World greeting."""\n    # Write your code here\n    return ""\n',
        },
    }

    problem, created = Problem.objects.get_or_create(
        contest=contest, code="HELLO", defaults=problem_defaults
    )

    # Attach a Python testcase from prepared file
    tc_path = os.path.join(os.path.dirname(__file__), "testcases", "python_hello.json")
    if os.path.exists(tc_path):
        with open(tc_path, "rb") as f:
            content = ContentFile(f.read(), name="python_hello.json")
            tc, _ = TestCase.objects.get_or_create(problem=problem, language="python")
            if not tc.file:
                tc.file.save("python_hello.json", content, save=True)
            tc.save()
    else:
        print(f"Testcase file not found at {tc_path}")

    print(
        f"Seeded problem: {problem.code} - {problem.title} in contest '{contest.name}'"
    )


if __name__ == "__main__":
    main()
