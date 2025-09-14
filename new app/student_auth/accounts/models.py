from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import os
import uuid
from django.db.models import JSONField

User = get_user_model()


# ----------------- Student Model -----------------
class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Stored as Django-compatible hash
    mobile = models.CharField(max_length=15)
    college = models.CharField(max_length=200)
    passout_year = models.IntegerField()
    branch = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ----------------- Participant Model -----------------
class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=120)
    handle = models.CharField(max_length=64, unique=True)
    is_disqualified = models.BooleanField(default=False)

    def __str__(self):
        return self.handle or self.name


# ----------------- Contest Model -----------------
class Contest(models.Model):
    name = models.CharField(max_length=200)
    start_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def end_at(self):
        return self.start_at + timezone.timedelta(minutes=self.duration_minutes)


# ----------------- Problem Model -----------------
class Problem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="problems")
    code = models.CharField(max_length=30)  # e.g., P1, P2
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)

    difficulty = models.CharField(
        max_length=20,
        choices=[("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")],
        default="Easy"
    )
    constraints = models.TextField(blank=True, null=True)
    
    # Function signature fields for stub generation
    function_name = models.CharField(max_length=100, blank=True, null=True, 
                                   help_text="Function name for starter code generation (e.g., 'add_numbers')")
    function_params = JSONField(default=list, blank=True,
                               help_text="List of parameter names (e.g., ['a', 'b'])")
    return_type = models.CharField(max_length=50, blank=True, null=True,
                                  help_text="Return type hint (e.g., 'int', 'List[int]')")
    
    # Pre-defined starter code stubs per language
    default_stub = JSONField(default=dict, blank=True,
                            help_text="Custom starter code by language (e.g., {'python': 'def solution():', 'java': 'public class Solution {}'})")


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["contest", "code"], name="uniq_problem_contest_code"),
        ]

    def __str__(self):
        return f"{self.contest.name}: {self.code} - {self.title}"


# ----------------- TestCase Model -----------------
def testcase_upload_path(instance, filename):
    """
    Custom path: media/testcases/problem_<id>/<language>_<filename>
    Example: media/testcases/problem_1/python_sample.json
    """
    return os.path.join(
        "testcases",
        f"problem_{instance.problem.id}",
        f"{instance.language}_{filename}"
    )


class TestCase(models.Model):
    LANGUAGE_CHOICES = [
        ("python", "Python"),
        ("cpp", "C++"),
        ("java", "Java"),
    ]

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="testcases")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    file = models.FileField(upload_to=testcase_upload_path)  # saved on server
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.problem.code} - {self.language}"


# ----------------- Submission Model -----------------
class UserSolution(models.Model):
    """Track which problems each student has solved"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="solutions")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="solutions")
    is_solved = models.BooleanField(default=False)
    solved_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    best_code = models.TextField(blank=True, null=True)  # Store the working solution
    language = models.CharField(max_length=20, default="python")
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "problem"], name="uniq_solution_student_problem"),
        ]
    
    def __str__(self):
        status = "✅ Solved" if self.is_solved else "❌ Unsolved"
        return f"{self.student.name} - {self.problem.title} ({status})"


# ----------------- Async Submissions -----------------
class Submission(models.Model):
    class Status(models.TextChoices):
        QUEUED = "QUEUED"
        RUNNING = "RUNNING"
        DONE = "DONE"
        ERROR = "ERROR"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions", null=True, blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="submissions")
    code = models.TextField()
    language = models.CharField(max_length=20, default="python")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.QUEUED)
    score = models.FloatField(default=0)
    max_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    judge0_tokens = JSONField(default=list, blank=True)
    judge0_raw = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Submission {self.id} - {self.status} ({self.score}/{self.max_score})"


class SubmissionTestCaseResult(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="results")
    index = models.PositiveIntegerField()
    group = models.CharField(max_length=50, default="default")
    weight = models.FloatField(default=1.0)
    stdin = models.TextField(blank=True, null=True)
    expected_output = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    passed = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default="Pending")
    time_ms = models.FloatField(default=0)
    memory_kb = models.IntegerField(default=0)
    judge0_raw = JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["submission", "index"], name="uniq_result_submission_index"),
        ]

    def __str__(self):
        return f"Result {self.submission_id}[{self.index}] - {'OK' if self.passed else 'WA'}"
