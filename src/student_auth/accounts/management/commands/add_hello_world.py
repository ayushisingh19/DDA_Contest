from django.core.management.base import BaseCommand
from django.utils import timezone
import json
import os
from accounts.models import Contest, Problem, TestCase


class Command(BaseCommand):
    help = "Add Hello World problem with test cases"

    def handle(self, *args, **options):
        # Create or get contest
        contest, created = Contest.objects.get_or_create(
            name="Practice Contest",
            defaults={
                "start_at": timezone.now(),
                "duration_minutes": 180,  # 3 hours
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created contest: {contest.name}"))

        # Create Hello World problem
        problem, created = Problem.objects.get_or_create(
            contest=contest,
            code="P1",
            defaults={
                "title": "Hello World",
                "description": """Write a program that prints "Hello, World!" to the console.

This is a simple introductory problem to test your setup and understanding of basic input/output.

Your program should output exactly: Hello, World!

Note: Make sure there are no extra spaces or characters in your output.""",
                "difficulty": "Easy",
                "constraints": """- No input required
- Output must be exactly "Hello, World!" (without quotes)
- No trailing spaces or newlines beyond what's required""",
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created problem: {problem.title}"))
        else:
            self.stdout.write(
                self.style.WARNING(f"Problem already exists: {problem.title}")
            )
            return

        # Create test cases directory
        testcase_dir = f"media/testcases/problem_{problem.id}"
        os.makedirs(testcase_dir, exist_ok=True)

        # Python test cases
        python_testcases = {
            "test_cases": [
                {
                    "test_case_no": 1,
                    "stdin": "",
                    "expected_output": "Hello, World!",
                    "is_visible": True,
                    "explanation": "Basic Hello World output",
                },
                {
                    "test_case_no": 2,
                    "stdin": "",
                    "expected_output": "Hello, World!",
                    "is_visible": False,
                    "explanation": "Hidden test case - same output",
                },
            ]
        }

        # C++ test cases
        cpp_testcases = {
            "test_cases": [
                {
                    "test_case_no": 1,
                    "stdin": "",
                    "expected_output": "Hello, World!",
                    "is_visible": True,
                    "explanation": "Basic Hello World output",
                },
                {
                    "test_case_no": 2,
                    "stdin": "",
                    "expected_output": "Hello, World!",
                    "is_visible": False,
                    "explanation": "Hidden test case - same output",
                },
            ]
        }

        # Save Python test cases
        python_file = os.path.join(testcase_dir, "python_testcases.json")
        with open(python_file, "w") as f:
            json.dump(python_testcases, f, indent=2)

        # Save C++ test cases
        cpp_file = os.path.join(testcase_dir, "cpp_testcases.json")
        with open(cpp_file, "w") as f:
            json.dump(cpp_testcases, f, indent=2)

        # Create TestCase model instances
        python_tc, created = TestCase.objects.get_or_create(
            problem=problem,
            language="python",
            defaults={
                "file": f"testcases/problem_{problem.id}/python_testcases.json",
                "is_hidden": False,
            },
        )

        cpp_tc, created = TestCase.objects.get_or_create(
            problem=problem,
            language="cpp",
            defaults={
                "file": f"testcases/problem_{problem.id}/cpp_testcases.json",
                "is_hidden": False,
            },
        )

        self.stdout.write(
            self.style.SUCCESS("✅ Hello World problem added successfully!")
        )
        self.stdout.write(self.style.SUCCESS(f"Python test cases: {python_file}"))
        self.stdout.write(self.style.SUCCESS(f"C++ test cases: {cpp_file}"))
        self.stdout.write(
            self.style.SUCCESS("You can now access the problem in the contest page.")
        )
