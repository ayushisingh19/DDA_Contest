import os
import sys
import django

# Add the project directory to Python path (updated path after reorg)
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
project_path = os.path.join(repo_root, "src", "student_auth")
if project_path not in sys.path:
    sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_auth.settings')

django.setup()

from accounts.models import Problem, TestCase, Submission, Student
from accounts.tasks import evaluate_submission

def test_submission_evaluation():
    print("🧪 Testing Submission Evaluation End-to-End")
    print("=" * 60)
    
    # Check if we have test data
    problem = Problem.objects.first()
    if not problem:
        print("❌ No problems found in database")
        return
    
    print(f"✅ Found problem: {problem.title}")
    
    # Check test cases
    testcases = TestCase.objects.filter(problem=problem)
    print(f"✅ Found {testcases.count()} test cases for this problem")
    
    for tc in testcases:
        print(f"   - {tc.language}: {tc.file}")
        
    # Check if we have students
    student = Student.objects.first()
    if not student:
        print("❌ No students found in database")
        return
        
    print(f"✅ Found student: {student.email}")
    
    # Create a test submission
    test_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    submission = Submission.objects.create(
        student=student,
        problem=problem,
        code=test_code,
        language='python'
    )
    
    print(f"✅ Created submission {submission.id}")
    
    # Test evaluation
    try:
        print("🔄 Evaluating submission...")
        result = evaluate_submission(str(submission.id))
        print(f"✅ Evaluation completed: {result}")
        
        # Refresh submission from database
        submission.refresh_from_db()
        print(f"📊 Final status: {submission.status}")
        print(f"📊 Score: {submission.score}/{submission.max_score}")
        
        if hasattr(submission, 'judge0_raw') and submission.judge0_raw:
            print(f"📊 Judge0 data: {submission.judge0_raw}")
            
        # Check results
        results = submission.results.all()
        print(f"📊 Test case results: {results.count()}")
        for result in results:
            print(f"   - Test {result.index}: {'✅ PASS' if result.passed else '❌ FAIL'}")
            
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_submission_evaluation()