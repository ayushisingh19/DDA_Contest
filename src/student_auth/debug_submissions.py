# ruff: noqa: E402
#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from accounts.models import Problem, TestCase, Submission

print("=== TESTING SUBMISSION FLOW ===")

# Check what problems exist
print("\n📋 Available Problems:")
for problem in Problem.objects.all():
    testcase_count_python = TestCase.objects.filter(
        problem=problem, language="python"
    ).count()
    testcase_count_cpp = TestCase.objects.filter(
        problem=problem, language="cpp"
    ).count()
    print(f"  Problem {problem.id}: {problem.title}")
    print(f"    Python test cases: {testcase_count_python}")
    print(f"    C++ test cases: {testcase_count_cpp}")

# Test the query that's failing
print("\n🔍 Testing TestCase Query for Each Problem:")
for problem in Problem.objects.all():
    for language in ["python", "cpp"]:
        testcases_qs = TestCase.objects.filter(problem=problem, language=language)
        testcase_count = testcases_qs.count()

        if testcase_count == 0:
            print(f"  ❌ Problem {problem.id} ({language}): NO TEST CASES FOUND")
            print(
                "      This would trigger: 'No test cases available for this problem'"
            )
        else:
            print(
                f"  ✅ Problem {problem.id} ({language}): {testcase_count} test cases found"
            )

# Let's also check if there are any submissions that might be pointing to non-existent problems
print("\n📤 Checking Existing Submissions:")
submissions = Submission.objects.all()
print(f"Total submissions: {submissions.count()}")

for sub in submissions:
    try:
        problem_id = sub.problem.id
        problem_title = sub.problem.title
        language = sub.language
        testcase_count = TestCase.objects.filter(
            problem=sub.problem, language=language
        ).count()

        if testcase_count == 0:
            print(
                f"  ❌ Submission {sub.id}: Problem {problem_id} ({problem_title}) - {language} - NO TEST CASES!"
            )
        else:
            print(
                f"  ✅ Submission {sub.id}: Problem {problem_id} ({problem_title}) - {language} - {testcase_count} test cases"
            )
    except Exception as e:
        print(f"  ❌ Submission {sub.id}: ERROR - {e}")

print("\n=== DIAGNOSIS COMPLETE ===")
print(
    "If you see any ❌ entries above, that's where the 'No test cases available' error is coming from!"
)
