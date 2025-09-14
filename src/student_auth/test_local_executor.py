# ruff: noqa: E402
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from accounts.models import Student, Problem, Submission


def test_fallback_simple():
    print("Testing Simple Internal Error Fallback")
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

    # Simple code that should work
    code = """def solution():
    return [0, 1]

print(solution())"""

    submission = Submission.objects.create(
        student=student, problem=problem, code=code, status=Submission.Status.QUEUED
    )

    print(f"Created submission ID: {submission.id}")
    print()

    # Test our LocalCodeExecutor directly
    from accounts.tasks import LocalCodeExecutor

    local_executor = LocalCodeExecutor()
    test_cases = [
        {"stdin": "2 7\n9", "expected_output": "[0, 1]"},
        {"stdin": "3 2 4\n6", "expected_output": "[1, 2]"},
        {"stdin": "3 3\n6", "expected_output": "[0, 1]"},
    ]

    print("Testing LocalCodeExecutor directly:")
    print("-" * 40)

    try:
        results = local_executor.execute_python_code(code, test_cases)
        for i, result in enumerate(results):
            status_symbol = "✅" if result["passed"] else "❌"
            print(f"{status_symbol} Test {i+1}: {result['status']}")
            print(f"   Expected: {result['expected_output']}")
            print(f"   Got: {result['output']}")
            print()
    except Exception as e:
        print(f"❌ LocalCodeExecutor failed: {e}")
        import traceback

        traceback.print_exc()

    print("✅ LocalCodeExecutor test completed")
    return submission


if __name__ == "__main__":
    test_fallback_simple()
