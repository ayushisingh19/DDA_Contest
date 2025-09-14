#!/usr/bin/env python
import os
import sys
import django
import json

# Add the project path (relative to repo root)
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'src', 'student_auth'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_auth.settings')
django.setup()

from accounts.models import Problem, TestCase, Contest

print("=== Finding Orphaned TestCase Files ===")

media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'src', 'student_auth', 'media')
testcases_dir = os.path.join(media_root, 'testcases')

orphaned_files = []

if os.path.exists(testcases_dir):
    for item in os.listdir(testcases_dir):
        if item.startswith('problem_'):
            problem_id = item.replace('problem_', '')
            try:
                problem_id = int(problem_id)
            except ValueError:
                print(f"❌ Invalid problem directory name: {item}")
                continue
            
            problem_dir = os.path.join(testcases_dir, item)
            if os.path.isdir(problem_dir):
                print(f"\n📁 Processing {item} (Problem ID: {problem_id})")
                
                # Check if problem exists
                try:
                    problem = Problem.objects.get(id=problem_id)
                    print(f"  ✅ Problem exists: {problem.title}")
                except Problem.DoesNotExist:
                    print(f"  ❌ Problem {problem_id} does not exist in database!")
                    for file in os.listdir(problem_dir):
                        file_path = os.path.join(problem_dir, file)
                        orphaned_files.append(file_path)
                    continue
                
                # Check each file in the directory
                for file in os.listdir(problem_dir):
                    file_path = os.path.join(problem_dir, file)
                    print(f"    📄 Found file: {file}")
                    
                    # Parse language from filename
                    if file.endswith('.json'):
                        # Extract language from filename pattern: language_whatever.json
                        parts = file.split('_')
                        if len(parts) >= 1:
                            language = parts[0]
                            print(f"      Detected language: {language}")
                            
                            # Check if TestCase entry exists
                            existing_testcase = TestCase.objects.filter(
                                problem=problem,
                                language=language,
                                file__icontains=file
                            ).first()
                            
                            if existing_testcase:
                                print(f"      ✅ TestCase entry exists in database")
                            else:
                                print(f"      ❌ NO TestCase entry in database!")
                                orphaned_files.append(file_path)
                                
                                # Try to create the missing entry
                                print(f"      🔧 Attempting to create TestCase entry...")
                                relative_path = os.path.join('testcases', item, file)
                                
                                try:
                                    testcase = TestCase.objects.create(
                                        problem=problem,
                                        language=language,
                                        file=relative_path
                                    )
                                    print(f"      ✅ Created TestCase entry: {testcase.id}")
                                except Exception as e:
                                    print(f"      ❌ Failed to create TestCase: {e}")

print(f"\n=== Summary ===")
print(f"Orphaned files found: {len(orphaned_files)}")
for file in orphaned_files:
    print(f"  - {file}")

print(f"\n=== Final TestCase Count ===")
for problem in Problem.objects.all():
    testcase_count = TestCase.objects.filter(problem=problem).count()
    print(f"Problem {problem.id} ({problem.title}): {testcase_count} testcases")