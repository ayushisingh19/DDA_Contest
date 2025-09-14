import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from accounts.models import Contest, Problem, TestCase


class Command(BaseCommand):
    help = "Create sample data for testing the coding platform"

    def handle(self, *args, **options):
        # Create a sample contest
        contest, created = Contest.objects.get_or_create(
            name="Sample Coding Contest",
            defaults={
                "start_at": datetime.now(),
                "duration_minutes": 120,
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created contest: {contest.name}"))
        else:
            self.stdout.write(f"📋 Contest already exists: {contest.name}")

        # Create a sample problem
        problem, created = Problem.objects.get_or_create(
            contest=contest,
            code="P1",
            defaults={
                "title": "Two Sum",
                "description": """Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

Example:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 2 + 7 == 9, we return [0, 1].""",
                "difficulty": "Easy",
                "constraints": """- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- Only one valid answer exists.""",
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Created problem: {problem.title}")
            )
        else:
            self.stdout.write(f"📋 Problem already exists: {problem.title}")

        # Create sample test case data
        python_test_data = {
            "metadata": {
                "problem_name": "two_sum",
                "language": "python",
                "language_id": 71,
                "total_test_cases": 3,
                "visible_cases": 3,
                "hidden_cases": 0,
                "tle_limit": 1.0,
                "mle_limit": 64000,
            },
            "test_cases": [
                {
                    "test_case_no": 1,
                    "stdin": "[2,7,11,15]\n9",
                    "expected_output": "[0,1]",
                    "is_visible": True,
                },
                {
                    "test_case_no": 2,
                    "stdin": "[3,2,4]\n6",
                    "expected_output": "[1,2]",
                    "is_visible": True,
                },
                {
                    "test_case_no": 3,
                    "stdin": "[3,3]\n6",
                    "expected_output": "[0,1]",
                    "is_visible": True,
                },
            ],
        }

        cpp_test_data = {
            "metadata": {
                "problem_name": "two_sum",
                "language": "cpp",
                "language_id": 54,
                "total_test_cases": 3,
                "visible_cases": 3,
                "hidden_cases": 0,
                "tle_limit": 1.0,
                "mle_limit": 64000,
            },
            "test_cases": [
                {
                    "test_case_no": 1,
                    "stdin": "[2,7,11,15]\n9",
                    "expected_output": "[0,1]",
                    "is_visible": True,
                },
                {
                    "test_case_no": 2,
                    "stdin": "[3,2,4]\n6",
                    "expected_output": "[1,2]",
                    "is_visible": True,
                },
                {
                    "test_case_no": 3,
                    "stdin": "[3,3]\n6",
                    "expected_output": "[0,1]",
                    "is_visible": True,
                },
            ],
        }

        # Python test case
        python_tc, created = TestCase.objects.get_or_create(
            problem=problem, language="python", defaults={}
        )

        if created or not python_tc.file:
            python_json = json.dumps(python_test_data, indent=2)
            python_tc.file.save(
                "python_two_sum_testcases.json", ContentFile(python_json), save=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Created Python test case file: {python_tc.file.path}"
                )
            )
        else:
            self.stdout.write(
                f"📋 Python test case already exists: {python_tc.file.path}"
            )

        # C++ test case
        cpp_tc, created = TestCase.objects.get_or_create(
            problem=problem, language="cpp", defaults={}
        )

        if created or not cpp_tc.file:
            cpp_json = json.dumps(cpp_test_data, indent=2)
            cpp_tc.file.save(
                "cpp_two_sum_testcases.json", ContentFile(cpp_json), save=True
            )
            self.stdout.write(
                self.style.SUCCESS(f"✅ Created C++ test case file: {cpp_tc.file.path}")
            )
        else:
            self.stdout.write(f"📋 C++ test case already exists: {cpp_tc.file.path}")

        self.stdout.write(self.style.SUCCESS("\n🎉 Sample data setup complete!"))
        self.stdout.write(f"📊 Contest: {contest.name}")
        self.stdout.write(f"🧩 Problem: {problem.title}")
        self.stdout.write(
            f"📁 Test cases: {TestCase.objects.filter(problem=problem).count()}"
        )
        self.stdout.write("\nYou can now:")
        self.stdout.write("1. Visit /problems/ to see the problems list")
        self.stdout.write("2. Click on 'Two Sum' to start coding")
        self.stdout.write("3. Write some code and click 'Run' to test")
