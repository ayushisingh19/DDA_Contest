#!/usr/bin/env python
import os
import sys
import django

# Add the project path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(repo_root, 'src', 'student_auth'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_auth.settings')
django.setup()

from accounts.models import Problem, TestCase

print("=== Database TestCase Analysis ===")

# Check all problems
problems = Problem.objects.all()
print(f"Total problems in database: {problems.count()}")

for problem in problems:
    print(f"\nProblem {problem.id}: {problem.title}")
    testcases = TestCase.objects.filter(problem=problem)
    print(f"  TestCase entries in DB: {testcases.count()}")
    
    for tc in testcases:
        print(f"    Language: {tc.language}")
        print(f"    File path: {tc.file.name if tc.file else 'No file'}")
        print(f"    File exists: {tc.file.path if tc.file and os.path.exists(tc.file.path) else 'No'}")
        print(f"    Is hidden: {tc.is_hidden}")

print("\n=== Media Directory Analysis ===")

media_root = os.path.join(repo_root, 'src', 'student_auth', 'media')
testcases_dir = os.path.join(media_root, 'testcases')

if os.path.exists(testcases_dir):
    print(f"Media testcases directory exists: {testcases_dir}")
    for item in os.listdir(testcases_dir):
        problem_dir = os.path.join(testcases_dir, item)
        if os.path.isdir(problem_dir):
            print(f"  {item}:")
            for file in os.listdir(problem_dir):
                file_path = os.path.join(problem_dir, file)
                print(f"    {file} (size: {os.path.getsize(file_path)} bytes)")
else:
    print(f"Media testcases directory does not exist: {testcases_dir}")

print("\n=== Specific Problem 1 Analysis ===")

try:
    problem1 = Problem.objects.get(id=1)
    print(f"Problem 1: {problem1.title}")
    
    # Check for python testcases
    python_testcases = TestCase.objects.filter(problem=problem1, language='python')
    print(f"Python testcases in DB: {python_testcases.count()}")
    
    for tc in python_testcases:
        print(f"  File: {tc.file.name}")
        if tc.file:
            print(f"  Full path: {tc.file.path}")
            print(f"  Exists: {os.path.exists(tc.file.path)}")
            
except Problem.DoesNotExist:
    print("Problem with ID 1 does not exist")