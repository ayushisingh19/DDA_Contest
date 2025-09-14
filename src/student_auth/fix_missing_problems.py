# ruff: noqa: E402
#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from accounts.models import Problem, Contest, TestCase

print("=== CREATING MISSING PROBLEMS ===")

# Get the existing contest
try:
    contest = Contest.objects.get(id=1)
    print(f"Using contest: {contest.name}")
except Contest.DoesNotExist:
    print("ERROR: No contest found!")
    exit(1)

# Define the missing problems based on test case files
missing_problems = [
    {
        "id": 3,
        "code": "P3",
        "title": "Merge K Sorted Lists",
        "difficulty": "Hard",
        "description": "Merge k sorted linked lists and return it as one sorted list.",
    },
    {
        "id": 6,
        "code": "P6",
        "title": "Two Sum (Duplicate)",
        "difficulty": "Easy",
        "description": "Given an array of integers and a target, return indices of two numbers that add up to target.",
    },
    {
        "id": 7,
        "code": "P7",
        "title": "Hello World",
        "difficulty": "Easy",
        "description": "Print 'Hello, World!' to standard output.",
    },
]

for prob_data in missing_problems:
    # Check if problem already exists
    if Problem.objects.filter(id=prob_data["id"]).exists():
        print(f"✅ Problem {prob_data['id']} already exists")
        continue

    # Create the problem
    problem = Problem.objects.create(
        id=prob_data["id"],
        contest=contest,
        code=prob_data["code"],
        title=prob_data["title"],
        difficulty=prob_data["difficulty"],
        description=prob_data["description"],
    )
    print(f"✅ Created Problem {problem.id}: {problem.title}")

print("\n=== RUNNING REINDEX TO CREATE TESTCASE RECORDS ===")
# Now run reindex command
from django.core.management import call_command

call_command("reindex_testcases")

print("\n=== FINAL VERIFICATION ===")
for problem in Problem.objects.all():
    testcase_count = TestCase.objects.filter(problem=problem).count()
    print(f"Problem {problem.id} ({problem.title}): {testcase_count} test cases")
