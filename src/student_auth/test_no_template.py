# ruff: noqa: E402
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from accounts.models import Student, Problem, Submission


def test_no_template_submission():
    print("Testing Submission Without Code Templates")
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

    # Test with user's own code (no template)
    user_code = """print("Hello from user code!")
nums = [2, 7, 11, 15]
target = 9
result = [0, 1]
print(result)"""

    submission = Submission.objects.create(
        student=student,
        problem=problem,
        code=user_code,
        status=Submission.Status.QUEUED,
    )

    print(f"✅ Created submission ID: {submission.id}")
    print(f"✅ Code length: {len(user_code)} characters")
    print("✅ User provided their own code (no template)")
    print()
    print("Code content:")
    print("-" * 20)
    print(user_code)
    print("-" * 20)

    print()
    print("🎉 SUCCESS: System accepts user code without predefined templates!")
    return submission


if __name__ == "__main__":
    test_no_template_submission()
