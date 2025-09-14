#!/usr/bin/env python
import os
import sys
import django
import json

# Add the project path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(repo_root, 'src', 'student_auth'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_auth.settings')
django.setup()

from accounts.models import Problem, TestCase, Submission

print("=== Simulating Exact Task Logic ===")

problem1 = Problem.objects.get(id=1)
language = "python"

print(f"Problem: {problem1.title}")
print(f"Language: {language}")

# This is the exact code from tasks.py
testcases_qs = TestCase.objects.filter(problem=problem1, language=language)
tests = []

print(f"\nFound {testcases_qs.count()} testcase entries")

for tc in testcases_qs:
    print(f"\nProcessing TestCase: {tc.id}")
    print(f"  File: {tc.file.name}")
    print(f"  File path: {tc.file.path}")
    print(f"  File exists: {os.path.exists(tc.file.path) if tc.file else False}")
    print(f"  Ends with .json: {tc.file.path.endswith('.json') if tc.file else False}")
    
    if not tc.file or not tc.file.path.endswith('.json'):
        print(f"  SKIPPED: No file or not .json")
        continue
    
    try:
        with open(tc.file.path, 'r') as f:
            data = json.load(f)
            print(f"  JSON loaded successfully")
            print(f"  Keys in JSON: {list(data.keys())}")
            
            test_cases = data.get('test_cases', [])
            print(f"  Test cases found: {len(test_cases)}")
            
            for i, case in enumerate(test_cases):
                test_data = {
                    "stdin": case.get('stdin', ''),
                    "expected_output": case.get('expected_output', ''),
                    "group": case.get('group', 'default'),
                    "weight": float(case.get('weight', 1.0)),
                }
                tests.append(test_data)
                print(f"    Case {i+1}: stdin='{test_data['stdin'][:50]}...', expected='{test_data['expected_output'][:50]}...'")
                
    except Exception as e:
        print(f"  ERROR parsing file: {e}")

print(f"\nFinal result: {len(tests)} test cases loaded")

if not tests:
    print("❌ NO TESTS FOUND - This would cause 'No testcases found' error")
else:
    print("✅ Tests loaded successfully")

print(f"\nTest cases summary:")
for i, test in enumerate(tests):
    print(f"  {i+1}. stdin='{test['stdin']}', expected='{test['expected_output']}', weight={test['weight']}")