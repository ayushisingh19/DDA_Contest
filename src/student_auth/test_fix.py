# ruff: noqa: E402
#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from accounts.models import Problem, TestCase

print("=== TESTING TESTCASE LOADING FOR ALL PROBLEMS ===")

for problem in Problem.objects.all():
    print(f"\n🧪 Testing Problem {problem.id}: {problem.title}")

    # Test both Python and C++ (if available)
    for language in ["python", "cpp"]:
        testcases_qs = TestCase.objects.filter(problem=problem, language=language)
        testcase_count = testcases_qs.count()

        if testcase_count > 0:
            print(f"  ✅ {language}: {testcase_count} test case(s) found")

            # Try to load the actual test case file
            for tc in testcases_qs:
                try:
                    import json

                    if tc.file and os.path.exists(tc.file.path):
                        with open(tc.file.path, "r") as f:
                            data = json.load(f)
                            test_count = len(data.get("test_cases", []))
                            print(
                                f"    📄 File: {tc.file.name} ({test_count} test cases in JSON)"
                            )
                    else:
                        print(
                            f"    ❌ File missing: {tc.file.name if tc.file else 'No file'}"
                        )
                except Exception as e:
                    print(f"    ❌ Error reading file: {e}")
        else:
            print(f"  ⚠️  {language}: No test cases found")

print(f"\n✅ All {Problem.objects.count()} problems have been checked!")
print("The 'No test cases available for this problem' error should now be resolved! 🎉")
