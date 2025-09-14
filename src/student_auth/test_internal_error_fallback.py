# ruff: noqa: E402
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from accounts.models import User, Problem, Submission, SubmissionTestCaseResult
from accounts.tasks import evaluate_submission


def test_internal_error_fallback():
    print("Testing Internal Error Fallback System")
    print("=" * 50)

    # Get or create a user
    user, created = User.objects.get_or_create(
        username="testuser", defaults={"email": "test@example.com"}
    )

    # Get the Two Sum problem
    try:
        problem = Problem.objects.get(slug="two-sum")
    except Problem.DoesNotExist:
        print("❌ Two Sum problem not found. Please run add_sample_data.py first")
        return

    # Create submission
    code = """def two_sum(nums, target):
    num_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    return []

# Read input
nums = list(map(int, input().split()))
target = int(input())

# Get result
result = two_sum(nums, target)
print(result)"""

    submission = Submission.objects.create(
        student=user, problem=problem, code=code, status=Submission.Status.PENDING
    )

    print(f"Created submission ID: {submission.id}")
    print(f"Problem: {problem.title}")
    print(f"Code length: {len(code)} characters")
    print()

    # Execute submission
    print("Executing submission (expecting Judge0 Internal Error)...")
    try:
        result = evaluate_submission(submission.id)
        print(f"Task completed with result: {result}")
    except Exception as e:
        print(f"❌ Task failed with error: {e}")
        return

    # Refresh submission from database
    submission.refresh_from_db()

    print()
    print("Submission Results:")
    print(f"Status: {submission.status}")
    print(f"Score: {submission.score}/{submission.max_score}")
    print(f"Judge0 Raw Data: {submission.judge0_raw}")
    print()

    # Check test case results
    results = SubmissionTestCaseResult.objects.filter(submission=submission).order_by(
        "index"
    )
    print(f"Test Case Results ({results.count()} results):")
    print("-" * 40)

    passed_count = 0
    for result in results:
        status_symbol = "✅" if result.passed else "❌"
        print(f"{status_symbol} Test {result.index + 1}: {result.status}")
        print(f"   Input: {result.stdin}")
        print(f"   Expected: {result.expected_output}")
        print(f"   Got: {result.output}")
        print(f"   Time: {result.time_ms}ms, Memory: {result.memory_kb}KB")
        print()

        if result.passed:
            passed_count += 1

    print(f"Summary: {passed_count}/{results.count()} tests passed")

    # Check if local fallback was used
    if submission.judge0_raw and submission.judge0_raw.get("local_execution"):
        print("✅ Local fallback system was triggered successfully!")
        print(f"Fallback reason: {submission.judge0_raw.get('fallback_reason')}")
    else:
        print("⚠️  Local fallback was not triggered - Judge0 may have worked")

    return submission


if __name__ == "__main__":
    submission = test_internal_error_fallback()
    print(f"\nTest completed. Submission ID: {submission.id}")
