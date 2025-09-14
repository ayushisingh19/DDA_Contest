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

print("=== Debugging TestCase Filter ===")

problem1 = Problem.objects.get(id=1)
relative_path = 'testcases/problem_1/python_python_two_sum_testcases.json'

print(f"Problem: {problem1}")
print(f"Looking for file: {relative_path}")

# Check exact filter used in management command
testcase = TestCase.objects.filter(
    problem=problem1,
    language='python',
    file=relative_path
).first()

print(f"Found testcase: {testcase}")

# Check all testcases for this problem
all_testcases = TestCase.objects.filter(problem=problem1)
print(f"\nAll testcases for problem 1:")
for tc in all_testcases:
    print(f"  ID: {tc.id}")
    print(f"  Language: {tc.language}")
    print(f"  File: {tc.file.name}")
    print(f"  File matches: {tc.file.name == relative_path}")
    print()

# Check with different filters
print("Testing different filter approaches:")

# Filter by file name only
by_file = TestCase.objects.filter(file=relative_path)
print(f"Filter by file only: {by_file.count()} results")

# Filter by file icontains
by_file_contains = TestCase.objects.filter(file__icontains='python_python_two_sum_testcases.json')
print(f"Filter by file contains: {by_file_contains.count()} results")

# Filter by problem and language only
by_problem_lang = TestCase.objects.filter(problem=problem1, language='python')
print(f"Filter by problem+language: {by_problem_lang.count()} results")