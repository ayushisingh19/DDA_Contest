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

from accounts.models import Problem, TestCase, Submission

print("=== Language Mismatch Analysis ===")

problem1 = Problem.objects.get(id=1)
print(f"Problem 1: {problem1.title}")

# Check TestCase languages
testcases = TestCase.objects.filter(problem=problem1)
print(f"\nTestCase languages in DB:")
for tc in testcases:
    print(f"  - {tc.language}")

# Check recent submissions
submissions = Submission.objects.filter(problem=problem1).order_by('-created_at')[:5]
print(f"\nRecent submission languages:")
for sub in submissions:
    print(f"  - {sub.language} (ID: {sub.id})")

# Test the exact filter from tasks.py
test_language = "python"
print(f"\nTesting filter: problem={problem1.id}, language='{test_language}'")
matching_testcases = TestCase.objects.filter(problem=problem1, language=test_language)
print(f"Matching testcases: {matching_testcases.count()}")

for tc in matching_testcases:
    print(f"  File: {tc.file.name}")
    print(f"  Path exists: {os.path.exists(tc.file.path)}")

# Test different language variations
test_languages = ["python", "python3", "py"]
for lang in test_languages:
    matching = TestCase.objects.filter(problem=problem1, language=lang)
    print(f"Language '{lang}': {matching.count()} matches")

print("\n=== TestCase File Content Analysis ===")
for tc in TestCase.objects.filter(problem=problem1):
    print(f"\nTestCase: {tc.language}")
    print(f"File: {tc.file.name}")
    if tc.file and os.path.exists(tc.file.path):
        try:
            with open(tc.file.path, 'r') as f:
                content = f.read()
                print(f"File size: {len(content)} bytes")
                print(f"First 200 chars: {content[:200]}...")
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("File does not exist!")