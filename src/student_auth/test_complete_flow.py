# ruff: noqa: E402
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from accounts.models import Student, Problem, Submission, SubmissionTestCaseResult


def test_complete_submission_flow():
    print("Testing Complete Submission Flow with Fallback")
    print("=" * 50)

    # Get first problem
    problem = Problem.objects.first()
    if not problem:
        print("❌ No problems found in database")
        return

    print(f"Using problem: {problem.title}")

    # Get or create a student
    student, created = Student.objects.get_or_create(
        email="test@example.com",
        defaults={
            "name": "Test Student",
            "mobile": "1234567890",
            "college": "Test College",
            "passout_year": 2024,
            "branch": "Computer Science",
            "password": "test123",
        },
    )

    # Create a working Two Sum solution
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
        student=student, problem=problem, code=code, status=Submission.Status.QUEUED
    )

    print(f"Created submission ID: {submission.id}")
    print(f"Code length: {len(code)} characters")
    print()

    # Execute submission using our task
    print("Executing submission (expecting Judge0 Internal Error -> Local Fallback)...")
    try:
        # Import the function directly to run synchronously
        from accounts.tasks import evaluate_submission

        # Call the function directly rather than as a Celery task
        result = evaluate_submission(submission.id)
        print(f"Task completed with result: {result}")
    except Exception as e:
        print(f"❌ Task failed with error: {e}")
        import traceback

        traceback.print_exc()
        return

    # Refresh submission from database
    submission.refresh_from_db()

    print()
    print("Submission Results:")
    print(f"Status: {submission.status}")
    print(f"Score: {submission.score}/{submission.max_score}")

    # Check if local fallback was used
    if submission.judge0_raw and submission.judge0_raw.get("local_execution"):
        print("✅ LOCAL FALLBACK SYSTEM WAS TRIGGERED!")
        print(f"Fallback reason: {submission.judge0_raw.get('fallback_reason')}")
        print()
    elif "Internal Error" in str(submission.judge0_raw):
        print("⚠️  Judge0 returned Internal Error but fallback was not triggered")
        print()
    else:
        print("ℹ️  Judge0 worked correctly - no fallback needed")
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

    # Print full submission data for debugging
    print("\nFull Submission Data for Analysis:")
    print(f"judge0_raw: {submission.judge0_raw}")

    return submission


if __name__ == "__main__":
    submission = test_complete_submission_flow()
    if submission:
        print(f"\nTest completed. Submission ID: {submission.id}")

        # Check if fallback was actually triggered
        if submission.judge0_raw and submission.judge0_raw.get("local_execution"):
            print("🎉 SUCCESS: Local fallback system is working!")
        else:
            print("🔍 INFO: Judge0 might be working or fallback not triggered")
