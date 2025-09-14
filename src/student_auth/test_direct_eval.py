# ruff: noqa: E402
#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from accounts.models import Problem, TestCase, Student, Submission
from accounts.tasks import evaluate_submission

print("=== DIRECT TEST OF SUBMISSION EVALUATION ===")

# Get a problem that has test cases
problem = Problem.objects.get(id=1)  # Two Sum
print(f"Testing with Problem {problem.id}: {problem.title}")

# Check test cases
testcases = TestCase.objects.filter(problem=problem, language="python")
print(f"Found {testcases.count()} Python test cases for this problem")

if testcases.count() > 0:
    # Get or create a student
    student, created = Student.objects.get_or_create(
        email="test@example.com",
        defaults={
            "name": "Test Student",
            "password": "dummy",
            "mobile": "1234567890",
            "college": "Test College",
            "passout_year": 2024,
            "branch": "CS",
        },
    )

    # Create a test submission
    submission = Submission.objects.create(
        student=student,
        problem=problem,
        code="""
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
""",
        language="python",
    )

    print(f"Created test submission: {submission.id}")
    print(f"Initial status: {submission.status}")

    # Try to evaluate it directly
    try:
        print("\n🧪 Testing direct evaluation...")
        result = evaluate_submission(str(submission.id))
        print(f"Evaluation result: {result}")

        # Refresh submission from database
        submission.refresh_from_db()
        print(f"Final status: {submission.status}")
        print(f"Score: {submission.score}/{submission.max_score}")

        if submission.status == Submission.Status.ERROR:
            print(f"ERROR: {submission.judge0_raw}")

            if "No test cases available" in str(submission.judge0_raw):
                print("❌ STILL GETTING 'No test cases available' ERROR!")
                print("The issue is NOT resolved.")
            else:
                print("✅ Different error - test cases are being found!")
        else:
            print("✅ SUCCESS! No 'test cases available' error!")

    except Exception as e:
        print(f"❌ Exception during evaluation: {e}")
        import traceback

        traceback.print_exc()
else:
    print("❌ No test cases found - this is the problem!")
