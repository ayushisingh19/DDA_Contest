import os
import sys
sys.path.append("src/student_auth")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_auth.settings')

import django
django.setup()

from accounts.models import TestCase

# Check what the management command sees
testcases_dir = "src/student_auth/media/testcases"
for item in os.listdir(testcases_dir):
    if item.startswith('problem_'):
        print(f"Directory name: '{item}'")
        problem_dir = os.path.join(testcases_dir, item)
        for file in os.listdir(problem_dir):
            if file.endswith('.json'):
                relative_path = os.path.join('testcases', item, file)
                print(f"  Management command would create path: '{relative_path}'")
                
                # Check what's actually in the database
                problem_id = int(item.replace('problem_', ''))
                tc = TestCase.objects.filter(problem_id=problem_id, file__endswith=file).first()
                if tc:
                    print(f"  Database has path: '{tc.file}'")
                    print(f"  Paths match: {relative_path == tc.file}")
                break
        break