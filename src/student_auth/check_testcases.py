# ruff: noqa: E402
#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
django.setup()

from accounts.models import TestCase, Problem

print("=== TESTCASE DATABASE ANALYSIS ===")
print(f"Total TestCases in database: {TestCase.objects.count()}")
print(f"Total Problems in database: {Problem.objects.count()}")

print("\n=== TESTCASES BY PROBLEM ===")
for tc in TestCase.objects.all():
    file_path = tc.file.name if tc.file else "No file"
    print(
        f"  Problem {tc.problem.id} ({tc.problem.title}) - Language: {tc.language} - File: {file_path}"
    )

print("\n=== PROBLEMS WITHOUT TESTCASES ===")
problems_without_testcases = Problem.objects.filter(testcases__isnull=True)
for p in problems_without_testcases:
    print(f"  Problem {p.id}: {p.title}")

print("\n=== MEDIA FILE CHECK ===")
import glob

media_files = glob.glob("media/testcases/**/*.json", recursive=True)
print(f"Found {len(media_files)} JSON files in media/testcases/")
for f in media_files:
    print(f"  {f}")
