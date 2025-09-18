import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from functools import wraps
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import hashlib
from django.contrib.auth.hashers import make_password, check_password

from .models import Student, Contest, Problem, Participant, UserSolution, Submission
from .models import TestCase
from .forms import ContestForm, ProblemForm, TestCaseFormSet
from .utils import PasswordResetToken
from .tasks import evaluate_submission
from .stub_generator import generate_starter_code

# --------------------- Authentication Decorator ---------------------

def student_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        student_id = request.session.get('student_id')
        if not student_id:
            request.session['next_url'] = request.path
            messages.info(request, "Please register and login to access this page.")
            return redirect('home')
        
        student = Student.objects.filter(id=student_id).first()
        if not student:
            request.session.flush()
            messages.error(request, "Session expired. Please login again.")
            return redirect('home')
            
        return view_func(request, *args, **kwargs)
    return wrapper

# --------------------- Student Auth ---------------------

def healthz(request):
    return JsonResponse({"status": "ok"})

def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        mobile = request.POST.get('mobile')
        college = request.POST.get('college')
        passout_year = request.POST.get('passout_year')
        branch = request.POST.get('branch')

        # Validation
        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')
        
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long!")
            return redirect('register')

        student = Student.objects.create(
            name=name, email=email, password=make_password(password),
            mobile=mobile, college=college,
            passout_year=passout_year, branch=branch
        )
        
        # Registration successful - redirect to login
        messages.success(request, f"Registration successful! Please login to continue.")
        return redirect('login')
    return render(request, 'accounts/register.html')


def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        student = Student.objects.filter(email=email).first()
        if not student or not check_password(password, student.password):
            messages.error(request, "Invalid credentials")
            return redirect('login')

        request.session['student_id'] = student.id
        # Redirect to intended destination or contest page
        next_url = request.session.pop('next_url', '/contest/')
        messages.success(request, f"Welcome back, {student.name}!")
        return redirect(next_url)
    return render(request, 'accounts/login.html')


def logout(request):
    request.session.flush()
    return redirect('home')


# --------------------- Password Reset Views ---------------------

def forgot_password(request):
    """Display forgot password form and handle email submission"""
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            messages.error(request, "Please enter your email address.")
            return redirect('forgot_password')
        
        try:
            student = Student.objects.get(email=email)
            
            # Generate secure reset token
            raw_token, reset_token = PasswordResetToken.create_token(student)
            
            # Create reset link (use HTTPS in production)
            reset_link = request.build_absolute_uri(
                reverse('reset_password', kwargs={'token': raw_token})
            )
            
            # Send email (configure email settings in settings.py)
            try:
                send_reset_email(student, reset_link)
                messages.success(
                    request, 
                    f"Password reset link has been sent to {email}. "
                    "Please check your inbox and follow the instructions. "
                    "The link will expire in 15 minutes."
                )
            except Exception as e:
                messages.error(request, "Failed to send email. Please try again later.")
                print(f"Email sending error: {e}")  # Log for debugging
                
        except Student.DoesNotExist:
            # Security: Don't reveal if email exists or not
            messages.success(
                request, 
                f"If {email} is registered, you will receive a password reset link shortly."
            )
        
        return redirect('forgot_password')
    
    return render(request, 'accounts/forgot_password.html')


def reset_password(request, token):
    """Handle password reset with token verification"""
    student, reset_token = PasswordResetToken.verify_token(token)
    
    if not student or not reset_token:
        messages.error(
            request, 
            "Invalid or expired reset link. Please request a new password reset."
        )
        return redirect('forgot_password')
    
    if request.method == "POST":
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'accounts/reset_password.html', {'token': token})
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/reset_password.html', {'token': token})
        
        # Update password (hashed)
        student.password = make_password(new_password)
        student.save()
        
        # Mark token as used
        reset_token.mark_as_used()
        
        messages.success(
            request, 
            "Password updated successfully! Please login with your new password."
        )
        return redirect('login')
    
    # Display reset form
    return render(request, 'accounts/reset_password.html', {
        'token': token,
        'student': student
    })


def send_reset_email(student, reset_link):
    """Send password reset email to student"""
    subject = "Password Reset - DDA Contests"
    
    message = f"""
Hi {student.name},

You requested a password reset for your DDA Contests account.

Click the link below to reset your password:
{reset_link}

This link will expire in 15 minutes for security reasons.

If you didn't request this reset, please ignore this email.

Best regards,
Decode Data Academy Team
    """
    
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #8b5cf6, #3b82f6); padding: 20px; border-radius: 10px 10px 0 0;">
            <h2 style="color: white; margin: 0;">Password Reset Request</h2>
        </div>
        <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
            <p>Hi <strong>{student.name}</strong>,</p>
            
            <p>You requested a password reset for your DDA Contests account.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background: linear-gradient(135deg, #8b5cf6, #3b82f6); 
                          color: white; 
                          padding: 12px 24px; 
                          text-decoration: none; 
                          border-radius: 8px; 
                          font-weight: bold;
                          display: inline-block;">
                    Reset My Password
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666;">
                <strong>Security Note:</strong> This link will expire in 15 minutes.
            </p>
            
            <p style="font-size: 14px; color: #666;">
                If you didn't request this reset, please ignore this email.
            </p>
            
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            
            <p style="font-size: 12px; color: #999;">
                Best regards,<br>
                Decode Data Academy Team
            </p>
        </div>
    </div>
    """
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[student.email],
        html_message=html_message,
        fail_silently=False
    )


def home(request):
    student_id = request.session.get('student_id')
    student = Student.objects.filter(id=student_id).first()
    return render(request, 'accounts/index.html', {'student': student})


@student_login_required
def contest(request):
    student_id = request.session.get('student_id')
    student = Student.objects.filter(id=student_id).first()
    return render(request, 'accounts/contest.html', {'student': student})


# --------------------- Admin Panel ---------------------

@staff_member_required
def admin_dashboard(request):
    return render(request, "accounts/admin_dashboard.html")


@staff_member_required
def create_contest(request):
    if request.method == "POST":
        cform = ContestForm(request.POST, prefix="contest")
        pform = ProblemForm(request.POST, prefix="problem")
        tformset = TestCaseFormSet(request.POST, prefix="testcases")

        if cform.is_valid() and pform.is_valid() and tformset.is_valid():
            with transaction.atomic():
                contest = cform.save()
                problem = pform.save(commit=False)
                problem.contest = contest
                problem.save()

                for tc in tformset.save(commit=False):
                    tc.problem = problem
                    tc.save()
            return redirect("admin_dashboard")
    else:
        cform = ContestForm(prefix="contest")
        pform = ProblemForm(prefix="problem")
        tformset = TestCaseFormSet(prefix="testcases")

    return render(request, "accounts/create_contest.html", {
        "cform": cform, "pform": pform, "tformset": tformset,
    })


@staff_member_required
def delete_contest(request):
    contests = Contest.objects.all()
    if request.method == "POST":
        cid = request.POST.get("contest_id")
        contest = get_object_or_404(Contest, id=cid)
        contest.delete()
        return redirect("admin_dashboard")
    return render(request, "accounts/delete_contest.html", {"contests": contests})


@staff_member_required
def partial_evaluate(request):
    contests = Contest.objects.all()
    return render(request, "accounts/evaluation.html", {"contests": contests})


# --------------------- Problem Pages ---------------------

@student_login_required
def start(request, id=None):
    student = Student.objects.get(id=request.session['student_id'])
    problems = Problem.objects.all().order_by("id")
    problem = None
    visible_testcases = []

    # Get solved problems for this student
    solved_problems = set(
        UserSolution.objects.filter(student=student, is_solved=True)
        .values_list('problem_id', flat=True)
    )

    # Add solved status to each problem
    for p in problems:
        p.is_solved = p.id in solved_problems

    if id:
        problem = get_object_or_404(Problem, id=id)
        # Fetch visible test cases
        for tc in problem.testcases.all():
            if tc.file and tc.file.path.endswith(".json"):
                with open(tc.file.path, "r") as f:
                    try:
                        data = json.load(f)
                        for case in data.get("test_cases", []):
                            if case.get("is_visible", False):
                                visible_testcases.append(case)
                    except Exception as e:
                        print("Error reading testcase JSON:", e)

    return render(request, "accounts/start.html", {
        "problems": problems,
        "problem": problem,
        "visible_testcases": visible_testcases,
    })


# ----------------- RUN CODE -----------------

@student_login_required
def run_code(request, problem_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
    try:
        problem = get_object_or_404(Problem, id=problem_id)
        student = Student.objects.get(id=request.session['student_id'])
        code = request.POST.get("code")
        language = request.POST.get("language", "python")
        if not code:
            return JsonResponse({"error": "code is required"}, status=400)
        
        # Track attempts
        us, created = UserSolution.objects.get_or_create(student=student, problem=problem, defaults={'attempts': 1})
        if not created:
            us.attempts += 1
            us.save()
        
        # Create async submission
        sub = Submission.objects.create(student=student, problem=problem, code=code, language=language)
        
        # Try to queue the task with proper error handling
        try:
            evaluate_submission.delay(str(sub.id))
        except Exception as e:
            # If Celery is not available, set submission to error state
            sub.status = Submission.Status.ERROR
            sub.judge0_raw = {"error": "Task queue unavailable", "details": str(e)}
            sub.save(update_fields=["status", "judge0_raw", "updated_at"])
            return JsonResponse({
                "submission_id": str(sub.id), 
                "status": sub.status,
                "error": "Code evaluation service is temporarily unavailable. Please try again later."
            }, status=503)
            
        return JsonResponse({"submission_id": str(sub.id), "status": sub.status})
        
    except Exception as e:
        return JsonResponse({
            "error": "An error occurred while processing your code. Please try again.",
            "details": str(e) if settings.DEBUG else None
        }, status=500)


def get_visible_testcases(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    visible_cases = []

    for tc in problem.testcases.all():
        if tc.file and tc.file.path.endswith(".json"):
            with open(tc.file.path, "r") as f:
                try:
                    data = json.load(f)
                    for case in data.get("test_cases", []):
                        if case.get("is_visible", False):
                            visible_cases.append({
                                "test_case_no": case.get("test_case_no"),
                                "stdin": case.get("stdin"),
                                "expected_output": case.get("expected_output")
                            })
                except Exception as e:
                    print("Error reading testcase JSON:", e)

    return JsonResponse({"visible_testcases": visible_cases})

 
# ----------------- Async API -----------------
@csrf_exempt
def create_submission(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST
    problem_id = data.get('problem_id')
    code = data.get('code')
    language = data.get('language', 'python')
    if not problem_id or not code:
        return JsonResponse({"error": "problem_id and code required"}, status=400)
    
    try:
        problem = get_object_or_404(Problem, id=problem_id)
        student_id = request.session.get('student_id')
        student = Student.objects.filter(id=student_id).first()
        sub = Submission.objects.create(student=student, problem=problem, code=code, language=language)
        
        # Try to queue the task with proper error handling
        try:
            evaluate_submission.delay(str(sub.id))
        except Exception as e:
            # If Celery is not available, set submission to error state
            sub.status = Submission.Status.ERROR
            sub.judge0_raw = {"error": "Task queue unavailable", "details": str(e)}
            sub.save(update_fields=["status", "judge0_raw", "updated_at"])
            return JsonResponse({
                "submission_id": str(sub.id), 
                "status": sub.status,
                "error": "Code evaluation service is temporarily unavailable. Please try again later."
            }, status=503)
            
        return JsonResponse({"submission_id": str(sub.id), "status": sub.status})
    except Exception as e:
        return JsonResponse({
            "error": "An error occurred while processing your submission. Please try again.",
            "details": str(e) if settings.DEBUG else None
        }, status=500)


def get_submission_status(request, submission_id):
    sub = get_object_or_404(Submission, id=submission_id)
    
    # Check for task errors and provide detailed error information
    if sub.status == Submission.Status.ERROR and sub.judge0_raw:
        error_info = sub.judge0_raw
        error_msg = error_info.get('error', 'Unknown error occurred')
        
        # Enhanced error handling with specific details
        if 'No test cases available' in error_msg or 'No TestCase records found' in error_info.get('details', ''):
            return JsonResponse({
                "id": str(sub.id),
                "status": sub.status,
                "score": sub.score or 0,
                "max_score": sub.max_score or 0,
                "results": [],
                "error": "No test cases available for this problem",
                "error_details": error_info.get('details', ''),
                "solved": False
            })
        elif 'No valid test cases could be loaded' in error_msg:
            file_errors = error_info.get('file_errors', [])
            return JsonResponse({
                "id": str(sub.id),
                "status": sub.status,
                "score": sub.score or 0,
                "max_score": sub.max_score or 0,
                "results": [],
                "error": "Test case loading failed",
                "error_details": f"Found test case records but couldn't load valid test cases. Errors: {'; '.join(file_errors)}",
                "solved": False
            })
        else:
            return JsonResponse({
                "id": str(sub.id),
                "status": sub.status,
                "score": sub.score or 0,
                "max_score": sub.max_score or 0,
                "results": [],
                "error": error_msg,
                "error_details": error_info.get('details', ''),
                "solved": False
            })
    
    results = [{
        "index": r.index,
        "group": r.group,
        "weight": r.weight,
        "status": r.status,
        "passed": r.passed,
        "time_ms": r.time_ms,
        "memory_kb": r.memory_kb,
        "output": r.output or "",
        "expected": r.expected_output or "",
    } for r in sub.results.order_by('index')]
    
    return JsonResponse({
        "id": str(sub.id),
        "status": sub.status,
        "score": sub.score,
        "max_score": sub.max_score,
        "results": results,
        "solved": sub.status == Submission.Status.DONE and sub.score == sub.max_score
    })


@csrf_exempt
def health_check(request):
    """Health check endpoint for the application and Judge0 connectivity"""
    try:
        # Check database connectivity
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check Judge0 connectivity  
        from .tasks import _check_judge0_connectivity
        judge0_ok, judge0_error = _check_judge0_connectivity()
        
        # Check Celery connectivity
        celery_ok = True
        celery_error = None
        try:
            # Test Celery broker connection without waiting for result backend
            from celery import current_app
            from kombu import Connection
            
            # Test broker connection
            broker_url = current_app.conf.broker_url
            with Connection(broker_url) as conn:
                conn.ensure_connection(max_retries=1)
            
            # Test result backend connection separately
            try:
                from redis import Redis
                import re
                result_url = current_app.conf.result_backend
                match = re.match(r'redis://([^:]+):(\d+)/(\d+)', result_url)
                if match:
                    host, port, db = match.group(1), int(match.group(2)), int(match.group(3))
                    r = Redis(host=host, port=port, db=db, socket_timeout=2)
                    r.ping()
            except Exception as backend_error:
                # Result backend failure shouldn't fail the health check
                # Task queueing will still work even if result retrieval fails
                pass
                
        except Exception as e:
            celery_ok = False
            celery_error = str(e)
        
        status = {
            "database": "ok",
            "judge0": "ok" if judge0_ok else "error",
            "celery": "ok" if celery_ok else "error",
            "overall": "ok" if judge0_ok and celery_ok else "degraded"
        }
        
        if not judge0_ok:
            status["judge0_error"] = judge0_error
        if not celery_ok:
            status["celery_error"] = celery_error
            
        return JsonResponse(status, status=200 if status["overall"] == "ok" else 503)
        
    except Exception as e:
        return JsonResponse({
            "database": "error",
            "error": str(e),
            "overall": "error"
        }, status=503)


def get_problem_detail(request, problem_id):
    """Get problem details with starter code for specified language"""
    try:
        problem = get_object_or_404(Problem, id=problem_id)
        language = request.GET.get('language', 'python').lower()
        
        # Generate or retrieve starter code
        starter_code = generate_starter_code(language, problem)
        
        # Get visible test cases
        visible_testcases = []
        for tc in problem.testcases.all():
            if tc.file and tc.file.path.endswith(".json"):
                try:
                    with open(tc.file.path, "r") as f:
                        data = json.load(f)
                        for case in data.get("test_cases", []):
                            if case.get("is_visible", False):
                                visible_testcases.append({
                                    "test_case_no": case.get("test_case_no"),
                                    "stdin": case.get("stdin"),
                                    "expected_output": case.get("expected_output")
                                })
                except Exception as e:
                    print(f"Error reading testcase JSON: {e}")
        
        # Check if student has solved this problem
        is_solved = False
        student_id = request.session.get('student_id')
        if student_id:
            student = Student.objects.filter(id=student_id).first()
            if student:
                solution = UserSolution.objects.filter(student=student, problem=problem, is_solved=True).first()
                is_solved = solution is not None
        
        return JsonResponse({
            "id": problem.id,
            "code": problem.code,
            "title": problem.title,
            "description": problem.description or "",
            "difficulty": problem.difficulty,
            "constraints": problem.constraints or "",
            "function_name": problem.function_name or "solution",
            "function_params": problem.function_params or [],
            "return_type": problem.return_type or "int",
            "starter_code": starter_code,
            "visible_testcases": visible_testcases,
            "is_solved": is_solved
        })
        
    except Exception as e:
        return JsonResponse({
            "error": "Failed to retrieve problem details",
            "details": str(e) if settings.DEBUG else None
        }, status=500)


@csrf_exempt  
def get_starter_code(request, problem_id):
    """Get starter code for a specific problem and language"""
    if request.method != 'GET':
        return JsonResponse({"error": "GET method required"}, status=405)
        
    try:
        problem = get_object_or_404(Problem, id=problem_id)
        language = request.GET.get('language', 'python')
        
        starter_code = generate_starter_code(language, problem)
        
        return JsonResponse({
            "language": language,
            "starter_code": starter_code,
            "function_name": problem.function_name or "solution",
            "function_params": problem.function_params or []
        })
        
    except Exception as e:
        return JsonResponse({
            "error": "Failed to generate starter code", 
            "details": str(e) if settings.DEBUG else None
        }, status=500)


