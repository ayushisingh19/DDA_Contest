# ruff: noqa: E402
#!/usr/bin/env python3
"""
Test the integrated fallback system by creating a submission through Django
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
import django

django.setup()

from accounts.models import Problem, Submission
from accounts.tasks import evaluate_submission


def test_submission_with_fallback():
    print("🧪 Testing submission with local fallback...")

    # Get the problem
    problem = Problem.objects.get(id=1)
    print(f"Testing with problem: {problem.title}")

    # Create a test submission
    code = """
import json
line1 = input().strip()
line2 = input().strip()

# Parse the array from JSON format
nums = json.loads(line1)
target = int(line2)

for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            print([i, j])
            break
"""

    submission = Submission.objects.create(
        problem=problem, code=code, language="python"
    )

    print(f"Created submission: {submission.id}")

    # Trigger evaluation (this will use Judge0 first, then fallback to local)
    result = evaluate_submission(str(submission.id))

    # Refresh from database
    submission.refresh_from_db()

    print("\nResults:")
    print(f"Status: {submission.status}")
    print(f"Score: {submission.score}/{submission.max_score}")

    if submission.results.exists():
        print("\nIndividual test results:")
        for result in submission.results.all():
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} Test {result.index + 1}: {result.status}")
            print(f"  Expected: {result.expected_output}")
            print(f"  Got:      {result.output}")
            if result.status == "Runtime Error":
                print("  Error: Check stderr")
    else:
        print("❌ No test results found")

    print(f"\nJudge0 Raw Data: {submission.judge0_raw}")


if __name__ == "__main__":
    test_submission_with_fallback()
