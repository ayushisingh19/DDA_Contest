import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Count, Min, Q
from django.contrib.admin.views.decorators import staff_member_required
from functools import wraps
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from .models import (
    Student,
    Contest,
    Problem,
    UserSolution,
    Submission,
    ContestAttempt,
    JuniorSubmission,
    SeniorSubmission,
    PracticeCategory,
    PracticeSubtopic,
    PracticeQuestion,
    PracticeOption,
)
from .forms import ContestForm, ProblemForm, TestCaseFormSet
from .utils import PasswordResetToken
from .tasks import evaluate_submission
from .stub_generator import generate_starter_code

# --------------------- Authentication Decorator ---------------------


def student_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        student_id = request.session.get("student_id")
        if not student_id:
            request.session["next_url"] = request.path
            messages.info(request, "Please register and login to access this page.")
            return redirect("home")

        student = Student.objects.filter(id=student_id).first()
        if not student:
            request.session.flush()
            messages.error(request, "Session expired. Please login again.")
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper


# --------------------- Student Auth ---------------------


def healthz(request):
    return JsonResponse({"status": "ok"})


def practice_home(request):
    """Show practice categories and subtopics (two-card style)."""
    categories = (
        PracticeCategory.objects.prefetch_related("subtopics")
        .all()
        .order_by("order", "name")
    )
    return render(
        request,
        "accounts/practice_home.html",
        {
            "categories": categories,
        },
    )


def practice_question(request, question_id):
    q = get_object_or_404(PracticeQuestion.objects.prefetch_related("options"), id=question_id, is_active=True)
    if request.method == "POST":
        picked = request.POST.get("option")
        correct = q.correct_option
        is_correct = str(correct.id) == picked if correct else False
        return JsonResponse(
            {
                "correct": is_correct,
                "explanation": q.explanation,
                "answer": correct.text if correct else None,
            }
        )
    return render(request, "accounts/practice_question.html", {"question": q})


def practice_subtopic(request, subtopic_id):
    subtopic = get_object_or_404(
        PracticeSubtopic.objects.select_related("category"), id=subtopic_id
    )
    questions = (
        subtopic.questions.filter(is_active=True)
        .prefetch_related("options")
        .order_by("id")
    )
    categories = (
        PracticeCategory.objects.prefetch_related("subtopics")
        .all()
        .order_by("order", "name")
    )
    return render(
        request,
        "accounts/practice_subtopic.html",
        {
            "subtopic": subtopic,
            "questions": questions,
            "categories": categories,
        },
    )


def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        mobile = request.POST.get("mobile")
        college = request.POST.get("college")
        passout_year = request.POST.get("passout_year")
        branch = request.POST.get("branch")

        # Validation
        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long!")
            return redirect("register")

        Student.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            mobile=mobile,
            college=college,
            passout_year=passout_year,
            branch=branch,
        )

        # Registration successful - redirect to login
        messages.success(request, "Registration successful! Please login to continue.")
        return redirect("login")
    return render(request, "accounts/register.html")


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        student = Student.objects.filter(email=email).first()
        if not student or not check_password(password, student.password):
            messages.error(request, "Invalid credentials")
            return redirect("login")

        request.session["student_id"] = student.id
        # Redirect to intended destination or contest page
        next_url = request.session.pop("next_url", "/contest/")
        messages.success(request, f"Welcome back, {student.name}!")
        return redirect(next_url)
    return render(request, "accounts/login.html")


def logout(request):
    request.session.flush()
    return redirect("home")


# --------------------- Password Reset Views ---------------------


def forgot_password(request):
    """Display forgot password form and handle email submission"""
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        if not email:
            messages.error(request, "Please enter your email address.")
            return redirect("forgot_password")

        try:
            student = Student.objects.get(email=email)

            # Generate secure reset token
            raw_token, reset_token = PasswordResetToken.create_token(student)

            # Create reset link (use HTTPS in production)
            reset_link = request.build_absolute_uri(
                reverse("reset_password", kwargs={"token": raw_token})
            )

            # Send email (configure email settings in settings.py)
            try:
                send_reset_email(student, reset_link)
                messages.success(
                    request,
                    f"Password reset link has been sent to {email}. "
                    "Please check your inbox and follow the instructions. "
                    "The link will expire in 15 minutes.",
                )
            except Exception as e:
                messages.error(request, "Failed to send email. Please try again later.")
                print(f"Email sending error: {e}")  # Log for debugging

        except Student.DoesNotExist:
            # Security: Don't reveal if email exists or not
            messages.success(
                request,
                f"If {email} is registered, you will receive a password reset link shortly.",
            )

        return redirect("forgot_password")

    return render(request, "accounts/forgot_password.html")


def reset_password(request, token):
    """Handle password reset with token verification"""
    student, reset_token = PasswordResetToken.verify_token(token)

    if not student or not reset_token:
        messages.error(
            request,
            "Invalid or expired reset link. Please request a new password reset.",
        )
        return redirect("forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Validation
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, "accounts/reset_password.html", {"token": token})

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/reset_password.html", {"token": token})

        # Update password (hashed)
        student.password = make_password(new_password)
        student.save()

        # Mark token as used
        reset_token.mark_as_used()

        messages.success(
            request,
            "Password updated successfully! Please login with your new password.",
        )
        return redirect("login")

    # Display reset form
    return render(
        request, "accounts/reset_password.html", {"token": token, "student": student}
    )


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
        fail_silently=False,
    )


def home(request):
    student_id = request.session.get("student_id")
    student = Student.objects.filter(id=student_id).first()
    return render(request, "accounts/home.html", {"student": student})


def sage_highlights(request):
    # Logged-in student (optional for navbar/personalization)
    student_id = request.session.get("student_id")
    student = Student.objects.filter(id=student_id).first()

    # Provide list of event photos (ensure corresponding files exist in static/img)
    # Name your files as: sage_event_1.jpg, sage_event_2.jpg, ...
    gallery_images = ["1", "2", "3", "4", "5"]

    # Winners extracted from screenshots provided by you
    junior_winners = [
        {"rank": 1, "name": "Ashi Gupta"},
        {"rank": 2, "name": "Ankit Kumar Singh"},
        {"rank": 3, "name": "Aniket Kumar"},
    ]
    senior_winners = [
        {"rank": 1, "name": "Rajveer Pratap Singh"},
        {"rank": 2, "name": "Suraj Yadav"},
        {"rank": 3, "name": "Kaushiki Kumari"},
    ]

    context = {
        "student": student,
        "gallery_images": gallery_images,
        "junior_winners": junior_winners,
        "senior_winners": senior_winners,
    }
    return render(request, "accounts/sage_highlights.html", context)


@student_login_required
def contest(request):
    student_id = request.session.get("student_id")
    student = Student.objects.filter(id=student_id).first()
    # Enable the start section only when there is an active contest
    start_enabled = Contest.objects.filter(is_active=True).exists()
    return render(
        request,
        "accounts/contest.html",
        {
            "student": student,
            "problems_url": reverse("problems"),
            "start_enabled": start_enabled,
            "show_leaderboard": False,
        },
    )


def contest_junior(request):
    student_id = request.session.get("student_id")
    student = Student.objects.filter(id=student_id).first()
    start_enabled = Contest.objects.filter(is_active=True).exists()
    return render(
        request,
        "accounts/contest.html",
        {
            "student": student,
            "problems_url": reverse("junior_problems"),
            "start_enabled": start_enabled,
            "show_leaderboard": False,
        },
    )


def contest_senior(request):
    student_id = request.session.get("student_id")
    student = Student.objects.filter(id=student_id).first()
    start_enabled = Contest.objects.filter(is_active=True).exists()
    return render(
        request,
        "accounts/contest.html",
        {
            "student": student,
            "problems_url": reverse("senior_problems"),
            "start_enabled": start_enabled,
            "show_leaderboard": False,
        },
    )


"""Removed earlier duplicate sage_highlights definition (now unified above)."""


# --------------------- Admin Panel ---------------------


@staff_member_required
def admin_dashboard(request):
    contests = Contest.objects.all().order_by("-id")[:20]
    return render(request, "accounts/admin_dashboard.html", {"contests": contests})


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

    return render(
        request,
        "accounts/create_contest.html",
        {
            "cform": cform,
            "pform": pform,
            "tformset": tformset,
        },
    )


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


@staff_member_required
def admin_leaderboard(request, contest_id: int):
    contest = get_object_or_404(Contest, id=contest_id)
    # Aggregate per-student stats for this contest, mirroring the API logic
    qs = (
        UserSolution.objects.filter(is_solved=True, problem__contest=contest)
        .select_related("student", "problem__contest")
        .only("student_id", "solved_at", "problem_id", "best_time_ms")
    )
    agg = {}
    for sol in qs:
        if not sol.solved_at:
            continue
        sid = sol.student_id
        if sid not in agg:
            agg[sid] = {
                "student": sol.student,
                "solved": 0,
                "total_time_s": 0.0,
                "total_best_time_ms": 0.0,
                "first_solve": None,
                "points": 0,
            }
        agg[sid]["solved"] += 1
        delta = (sol.solved_at - contest.start_at).total_seconds() if contest.start_at and sol.solved_at else 0
        if delta < 0:
            delta = 0
        agg[sid]["total_time_s"] += float(delta)
        if sol.best_time_ms:
            agg[sid]["total_best_time_ms"] += float(sol.best_time_ms or 0.0)
        if not agg[sid]["first_solve"] or sol.solved_at < agg[sid]["first_solve"]:
            agg[sid]["first_solve"] = sol.solved_at
        agg[sid]["points"] += 1

    rows = [
        {
            "student_id": sid,
            "name": data["student"].name,
            "email": data["student"].email,
            "solved": data["solved"],
            "total_time_s": round(data["total_time_s"], 3),
            "total_best_time_ms": round(data["total_best_time_ms"], 3),
            "points": data["points"],
            "first_solve_at": data["first_solve"],
        }
        for sid, data in agg.items()
    ]
    rows.sort(
        key=lambda r: (
            -r["solved"],
            r["total_best_time_ms"],
            r["total_time_s"],
            r["student_id"],
        )
    )

    # Assign ranks with ties
    rank = 0
    prev_key = None
    for r in rows:
        key = (r["solved"], r["total_best_time_ms"], r["total_time_s"])
        if key != prev_key:
            rank = rows.index(r) + 1
            prev_key = key
        r["rank"] = rank

    return render(
        request,
        "accounts/leaderboard_admin.html",
        {"contest": contest, "rows": rows},
    )


@staff_member_required
def admin_leaderboard_csv(request, contest_id: int):
    contest = get_object_or_404(Contest, id=contest_id)
    # Reuse computation by calling the HTML view logic in a minimal way
    # (duplicate small block to avoid coupling to response rendering)
    qs = (
        UserSolution.objects.filter(is_solved=True, problem__contest=contest)
        .select_related("student", "problem__contest")
        .only("student_id", "solved_at", "problem_id", "best_time_ms")
    )
    agg = {}
    for sol in qs:
        if not sol.solved_at:
            continue
        sid = sol.student_id
        if sid not in agg:
            agg[sid] = {
                "student": sol.student,
                "solved": 0,
                "total_time_s": 0.0,
                "total_best_time_ms": 0.0,
                "first_solve": None,
                "points": 0,
            }
        agg[sid]["solved"] += 1
        delta = (sol.solved_at - contest.start_at).total_seconds() if contest.start_at and sol.solved_at else 0
        if delta < 0:
            delta = 0
        agg[sid]["total_time_s"] += float(delta)
        if sol.best_time_ms:
            agg[sid]["total_best_time_ms"] += float(sol.best_time_ms or 0.0)
        if not agg[sid]["first_solve"] or sol.solved_at < agg[sid]["first_solve"]:
            agg[sid]["first_solve"] = sol.solved_at
        agg[sid]["points"] += 1

    rows = [
        {
            "student_id": sid,
            "name": data["student"].name,
            "email": data["student"].email,
            "solved": data["solved"],
            "total_time_s": round(data["total_time_s"], 3),
            "total_best_time_ms": round(data["total_best_time_ms"], 3),
            "points": data["points"],
            "first_solve_at": data["first_solve"],
        }
        for sid, data in agg.items()
    ]
    rows.sort(
        key=lambda r: (
            -r["solved"],
            r["total_best_time_ms"],
            r["total_time_s"],
            r["student_id"],
        )
    )

    # Assign ranks with ties
    rank = 0
    prev_key = None
    for r in rows:
        key = (r["solved"], r["total_best_time_ms"], r["total_time_s"])
        if key != prev_key:
            rank = rows.index(r) + 1
            prev_key = key
        r["rank"] = rank

    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename=leaderboard_{contest.id}.csv"
    writer = csv.writer(response)
    writer.writerow([
        "Rank",
        "Student ID",
        "Name",
        "Email",
        "Solved",
        "Points",
        "Total Best Time (ms)",
        "Total Time (s)",
        "First Solve At",
    ])
    for r in rows:
        writer.writerow([
            r.get("rank"),
            r.get("student_id"),
            r.get("name"),
            r.get("email"),
            r.get("solved"),
            r.get("points"),
            r.get("total_best_time_ms"),
            r.get("total_time_s"),
            r.get("first_solve_at").isoformat() if r.get("first_solve_at") else "",
        ])

    return response


# --------------------- Problem Pages ---------------------


@student_login_required
def start(request, id=None):
    student = Student.objects.get(id=request.session["student_id"])
    problems = Problem.objects.all().order_by("id")
    problem = None
    visible_testcases = []
    # Attempt policy: One attempt per student. If the last attempt is over/locked, do NOT create another.
    latest_attempt = (
        ContestAttempt.objects.filter(student=student).order_by("-start_at").first()
    )
    if latest_attempt and (latest_attempt.is_over or latest_attempt.is_locked):
        return render(
            request,
            "accounts/contest_ended.html",
            {"student": student, "ended_at": latest_attempt.ended_at or latest_attempt.end_at},
        )
    # If no attempt exists yet, create a fresh one (1 hour default)
    attempt = latest_attempt or ContestAttempt.objects.create(student=student, duration_minutes=60)

    # Get solved problems for this student
    solved_problems = set(
        UserSolution.objects.filter(student=student, is_solved=True).values_list(
            "problem_id", flat=True
        )
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

    return render(
        request,
        "accounts/start.html",
        {
            "problems": problems,
            "problem": problem,
            "visible_testcases": visible_testcases,
            "contest_end_at": attempt.end_at,
            "contest_locked": attempt.is_locked or attempt.is_over,
            "student_id": student.id,
        },
    )


@student_login_required
def start_junior(request, id=None):
    student = Student.objects.get(id=request.session["student_id"])
    contest = Contest.objects.filter(name__icontains="junior").first()
    problems = Problem.objects.filter(contest=contest).order_by("id") if contest else Problem.objects.none()
    problem = None
    visible_testcases = []

    latest_attempt = (
        ContestAttempt.objects.filter(student=student).order_by("-start_at").first()
    )
    if latest_attempt and (latest_attempt.is_over or latest_attempt.is_locked):
        return render(
            request,
            "accounts/contest_ended.html",
            {"student": student, "ended_at": latest_attempt.ended_at or latest_attempt.end_at},
        )
    attempt = latest_attempt or ContestAttempt.objects.create(student=student, duration_minutes=60, contest=contest)
    if attempt.contest_id is None and contest:
        attempt.contest = contest
        attempt.save(update_fields=["contest"]) 

    solved_problems = set(
        UserSolution.objects.filter(student=student, is_solved=True).values_list(
            "problem_id", flat=True
        )
    )
    for p in problems:
        p.is_solved = p.id in solved_problems

    if id:
        problem = get_object_or_404(Problem, id=id, contest=contest)
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

    return render(
        request,
        "accounts/start.html",
        {
            "problems": problems,
            "problem": problem,
            "visible_testcases": visible_testcases,
            "contest_end_at": attempt.end_at,
            "contest_locked": attempt.is_locked or attempt.is_over,
            "student_id": student.id,
        },
    )


@student_login_required
def start_senior(request, id=None):
    student = Student.objects.get(id=request.session["student_id"])
    contest = Contest.objects.filter(name__icontains="senior").first()
    problems = Problem.objects.filter(contest=contest).order_by("id") if contest else Problem.objects.none()
    problem = None
    visible_testcases = []

    latest_attempt = (
        ContestAttempt.objects.filter(student=student).order_by("-start_at").first()
    )
    if latest_attempt and (latest_attempt.is_over or latest_attempt.is_locked):
        return render(
            request,
            "accounts/contest_ended.html",
            {"student": student, "ended_at": latest_attempt.ended_at or latest_attempt.end_at},
        )
    attempt = latest_attempt or ContestAttempt.objects.create(student=student, duration_minutes=60, contest=contest)
    if attempt.contest_id is None and contest:
        attempt.contest = contest
        attempt.save(update_fields=["contest"]) 

    solved_problems = set(
        UserSolution.objects.filter(student=student, is_solved=True).values_list(
            "problem_id", flat=True
        )
    )
    for p in problems:
        p.is_solved = p.id in solved_problems

    if id and contest:
        problem = get_object_or_404(Problem, id=id, contest=contest)
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

    return render(
        request,
        "accounts/start.html",
        {
            "problems": problems,
            "problem": problem,
            "visible_testcases": visible_testcases,
            "contest_end_at": attempt.end_at,
            "contest_locked": attempt.is_locked or attempt.is_over,
            "student_id": student.id,
        },
    )


# ----------------- RUN CODE -----------------


@student_login_required
def run_code(request, problem_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        # Server-side timing enforcement
        student = Student.objects.get(id=request.session["student_id"])
        # Ensure there is an active attempt; create one if missing
        attempt = ContestAttempt.objects.filter(student=student).order_by("-start_at").first()
        if not attempt:
            attempt = ContestAttempt.objects.create(
                student=student,
                duration_minutes=60,
                contest=problem.contest,
            )
        elif attempt.is_over or attempt.is_locked:
            return JsonResponse({"error": "Contest is over"}, status=403)

        problem = get_object_or_404(Problem, id=problem_id)
        code = request.POST.get("code")
        language = request.POST.get("language", "python")
        if not code:
            return JsonResponse({"error": "code is required"}, status=400)

        # Track attempts
        us, created = UserSolution.objects.get_or_create(
            student=student, problem=problem, defaults={"attempts": 1}
        )
        if not created:
            us.attempts += 1
            us.save()

        # Create async submission
        sub = Submission.objects.create(
            student=student, problem=problem, code=code, language=language
        )

        # Mirror into per-track table when applicable (based on problem's contest name)
        cname = (problem.contest.name or "").lower() if problem.contest_id else ""
        if "junior" in cname:
            JuniorSubmission.objects.create(
                orig_submission=sub.id,
                student=student,
                problem=problem,
                code=code,
                language=language,
                status=sub.status,
                score=0,
                max_score=0,
                judge0_tokens=[],
                judge0_raw={},
            )
        elif "senior" in cname:
            SeniorSubmission.objects.create(
                orig_submission=sub.id,
                student=student,
                problem=problem,
                code=code,
                language=language,
                status=sub.status,
                score=0,
                max_score=0,
                judge0_tokens=[],
                judge0_raw={},
            )

        # Try to queue the task with proper error handling
        try:
            evaluate_submission.delay(str(sub.id))
        except Exception as e:
            # If Celery is not available, set submission to error state
            sub.status = Submission.Status.ERROR
            sub.judge0_raw = {"error": "Task queue unavailable", "details": str(e)}
            sub.save(update_fields=["status", "judge0_raw", "updated_at"])
            return JsonResponse(
                {
                    "submission_id": str(sub.id),
                    "status": sub.status,
                    "error": "Code evaluation service is temporarily unavailable. Please try again later.",
                },
                status=503,
            )

        return JsonResponse({"submission_id": str(sub.id), "status": sub.status})

    except Exception as e:
        return JsonResponse(
            {
                "error": "An error occurred while processing your code. Please try again.",
                "details": str(e) if settings.DEBUG else None,
            },
            status=500,
        )


@student_login_required
def end_contest(request):
    """Manually end the contest for the current student (used by Submit button)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        student = Student.objects.get(id=request.session["student_id"])
        attempt = (
            ContestAttempt.objects.filter(student=student).order_by("-start_at").first()
        )
        if not attempt:
            attempt = ContestAttempt.objects.create(student=student, duration_minutes=60)
        if not attempt.ended_at:
            attempt.ended_at = timezone.now()
            attempt.ended_reason = request.POST.get("reason", "manual")
            attempt.is_locked = True
            attempt.save(update_fields=["ended_at", "ended_reason", "is_locked"])
        return JsonResponse({"ok": True, "ended_at": attempt.ended_at.isoformat()})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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
                            visible_cases.append(
                                {
                                    "test_case_no": case.get("test_case_no"),
                                    "stdin": case.get("stdin"),
                                    "expected_output": case.get("expected_output"),
                                }
                            )
                except Exception as e:
                    print("Error reading testcase JSON:", e)

    return JsonResponse({"visible_testcases": visible_cases})


def list_problems(request):
    """Return a list of problems for the current contest page view.
    Includes id, code, title, difficulty, and solved status for the logged-in student (if any).
    """
    try:
        student_id = request.session.get("student_id")
        student = Student.objects.filter(id=student_id).first() if student_id else None

        variant = request.GET.get("variant")
        if variant == "junior":
            contest = Contest.objects.filter(name__icontains="junior").first()
            problems = Problem.objects.filter(contest=contest).order_by("id") if contest else Problem.objects.none()
        elif variant == "senior":
            contest = Contest.objects.filter(name__icontains="senior").first()
            problems = Problem.objects.filter(contest=contest).order_by("id") if contest else Problem.objects.none()
        else:
            problems = Problem.objects.all().order_by("id")
        solved_ids = set()
        if student:
            solved_ids = set(
                UserSolution.objects.filter(student=student, is_solved=True).values_list(
                    "problem_id", flat=True
                )
            )

        data = [
            {
                "id": p.id,
                "code": p.code,
                "title": p.title,
                "difficulty": p.difficulty,
                "is_solved": p.id in solved_ids,
            }
            for p in problems
        ]
        return JsonResponse({"problems": data})
    except Exception as e:
        return JsonResponse(
            {"error": "Failed to load problems", "details": str(e) if settings.DEBUG else None},
            status=500,
        )


# ----------------- Async API -----------------
@csrf_exempt
def create_submission(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST
    problem_id = data.get("problem_id")
    code = data.get("code")
    language = data.get("language", "python")
    if not problem_id or not code:
        return JsonResponse({"error": "problem_id and code required"}, status=400)

    try:
        problem = get_object_or_404(Problem, id=problem_id)
        student_id = request.session.get("student_id")
        student = Student.objects.filter(id=student_id).first()
        sub = Submission.objects.create(
            student=student, problem=problem, code=code, language=language
        )

        # Try to queue the task with proper error handling
        try:
            evaluate_submission.delay(str(sub.id))
        except Exception as e:
            # If Celery is not available, set submission to error state
            sub.status = Submission.Status.ERROR
            sub.judge0_raw = {"error": "Task queue unavailable", "details": str(e)}
            sub.save(update_fields=["status", "judge0_raw", "updated_at"])
            return JsonResponse(
                {
                    "submission_id": str(sub.id),
                    "status": sub.status,
                    "error": "Code evaluation service is temporarily unavailable. Please try again later.",
                },
                status=503,
            )

        return JsonResponse({"submission_id": str(sub.id), "status": sub.status})
    except Exception as e:
        return JsonResponse(
            {
                "error": "An error occurred while processing your submission. Please try again.",
                "details": str(e) if settings.DEBUG else None,
            },
            status=500,
        )


def get_submission_status(request, submission_id):
    sub = get_object_or_404(Submission, id=submission_id)

    # Check for task errors and provide detailed error information
    if sub.status == Submission.Status.ERROR and sub.judge0_raw:
        error_info = sub.judge0_raw
        error_msg = error_info.get("error", "Unknown error occurred")

        # Enhanced error handling with specific details
        if (
            "No test cases available" in error_msg
            or "No TestCase records found" in error_info.get("details", "")
        ):
            return JsonResponse(
                {
                    "id": str(sub.id),
                    "status": sub.status,
                    "score": sub.score or 0,
                    "max_score": sub.max_score or 0,
                    "results": [],
                    "error": "No test cases available for this problem",
                    "error_details": error_info.get("details", ""),
                    "solved": False,
                }
            )
        elif "No valid test cases could be loaded" in error_msg:
            file_errors = error_info.get("file_errors", [])
            return JsonResponse(
                {
                    "id": str(sub.id),
                    "status": sub.status,
                    "score": sub.score or 0,
                    "max_score": sub.max_score or 0,
                    "results": [],
                    "error": "Test case loading failed",
                    "error_details": f"Found test case records but couldn't load valid test cases. Errors: {'; '.join(file_errors)}",
                    "solved": False,
                }
            )
        else:
            return JsonResponse(
                {
                    "id": str(sub.id),
                    "status": sub.status,
                    "score": sub.score or 0,
                    "max_score": sub.max_score or 0,
                    "results": [],
                    "error": error_msg,
                    "error_details": error_info.get("details", ""),
                    "solved": False,
                }
            )

    results = [
        {
            "index": r.index,
            "group": r.group,
            "weight": r.weight,
            "status": r.status,
            "passed": r.passed,
            "time_ms": r.time_ms,
            "memory_kb": r.memory_kb,
            "output": r.output or "",
            "expected": r.expected_output or "",
        }
        for r in sub.results.order_by("index")
    ]

    return JsonResponse(
        {
            "id": str(sub.id),
            "status": sub.status,
            "score": sub.score,
            "max_score": sub.max_score,
            "results": results,
            "solved": sub.status == Submission.Status.DONE
            and sub.score == sub.max_score,
        }
    )


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
                match = re.match(r"redis://([^:]+):(\d+)/(\d+)", result_url)
                if match:
                    host, port, db = (
                        match.group(1),
                        int(match.group(2)),
                        int(match.group(3)),
                    )
                    r = Redis(host=host, port=port, db=db, socket_timeout=2)
                    r.ping()
            except Exception:
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
            "overall": "ok" if judge0_ok and celery_ok else "degraded",
        }

        if not judge0_ok:
            status["judge0_error"] = judge0_error
        if not celery_ok:
            status["celery_error"] = celery_error

        return JsonResponse(status, status=200 if status["overall"] == "ok" else 503)

    except Exception as e:
        return JsonResponse(
            {"database": "error", "error": str(e), "overall": "error"}, status=503
        )


def get_problem_detail(request, problem_id):
    """Get problem details with starter code for specified language"""
    try:
        problem = get_object_or_404(Problem, id=problem_id)
        language = request.GET.get("language", "python").lower()

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
                                visible_testcases.append(
                                    {
                                        "test_case_no": case.get("test_case_no"),
                                        "stdin": case.get("stdin"),
                                        "expected_output": case.get("expected_output"),
                                    }
                                )
                except Exception as e:
                    print(f"Error reading testcase JSON: {e}")

        # Check if student has solved this problem
        is_solved = False
        student_id = request.session.get("student_id")
        if student_id:
            student = Student.objects.filter(id=student_id).first()
            if student:
                solution = UserSolution.objects.filter(
                    student=student, problem=problem, is_solved=True
                ).first()
                is_solved = solution is not None

        return JsonResponse(
            {
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
                "is_solved": is_solved,
            }
        )

    except Http404:
        return JsonResponse(
            {
                "error": "Problem not found",
                "problem_id": problem_id,
            },
            status=404,
        )
    except Exception as e:
        return JsonResponse(
            {
                "error": "Failed to retrieve problem details",
                "details": str(e) if settings.DEBUG else None,
            },
            status=500,
        )


@csrf_exempt
def get_starter_code(request, problem_id):
    """Get starter code for a specific problem and language"""
    if request.method != "GET":
        return JsonResponse({"error": "GET method required"}, status=405)

    try:
        problem = get_object_or_404(Problem, id=problem_id)
        language = request.GET.get("language", "python")

        starter_code = generate_starter_code(language, problem)

        return JsonResponse(
            {
                "language": language,
                "starter_code": starter_code,
                "function_name": problem.function_name or "solution",
                "function_params": problem.function_params or [],
            }
        )
    except Http404:
        return JsonResponse(
            {
                "error": "Problem not found",
                "problem_id": problem_id,
            },
            status=404,
        )
    except Exception as e:
        # Be resilient for consumers: return a safe fallback stub with the requested language
        language = request.GET.get("language", "python")
        fallback = generate_starter_code(
            language,
            None,
            function_name="solution",
            params=[],
            return_type="int",
            problem_title=None,
        )
        return JsonResponse(
            {
                "language": language,
                "starter_code": fallback,
                "function_name": "solution",
                "function_params": [],
                "warning": "Fallback starter code returned due to an internal error",
                "details": str(e) if settings.DEBUG else None,
            }
        )


def leaderboard(request):
    """Return leaderboard.
    Sort by problems solved (desc) and time taken (asc).
    If a contest_id is provided, compute total time as the sum of (solve_time - contest.start_at)
    across solved problems. Otherwise, use earliest solve time as a tie-breaker.
    """
    try:
        contest_id = request.GET.get("contest_id")

        if contest_id:
            contest = get_object_or_404(Contest, id=contest_id)
            # Gather solved solutions in this contest
            qs = (
                UserSolution.objects.filter(is_solved=True, problem__contest=contest)
                .select_related("student", "problem__contest")
                .only("student_id", "solved_at", "problem_id")
            )
            agg = {}
            for sol in qs:
                if not sol.solved_at:
                    continue
                sid = sol.student_id
                if sid not in agg:
                    agg[sid] = {
                        "student": sol.student,
                        "solved": 0,
                        # Sum of time deltas from contest start (seconds) for solved problems
                        "total_time_s": 0.0,
                        # Sum of fastest AC times across problems (milliseconds)
                        "total_best_time_ms": 0.0,
                        "first_solve": None,
                        # simple points: 1 per solved; can be extended later
                        "points": 0,
                    }
                agg[sid]["solved"] += 1
                delta = (sol.solved_at - contest.start_at).total_seconds()
                if delta < 0:
                    delta = 0
                agg[sid]["total_time_s"] += float(delta)
                if sol.best_time_ms:
                    agg[sid]["total_best_time_ms"] += float(sol.best_time_ms or 0.0)
                if not agg[sid]["first_solve"] or sol.solved_at < agg[sid]["first_solve"]:
                    agg[sid]["first_solve"] = sol.solved_at
                agg[sid]["points"] += 1

            # Build list and sort: solved desc, total_time asc, id asc
            rows = [
                {
                    "student_id": sid,
                    "name": data["student"].name,
                    "email": data["student"].email,
                    "solved": data["solved"],
                    "total_time_s": round(data["total_time_s"], 3),
                    "total_best_time_ms": round(data["total_best_time_ms"], 3),
                    "points": data["points"],
                    "first_solve_at": data["first_solve"].isoformat()
                    if data["first_solve"]
                    else None,
                }
                for sid, data in agg.items()
            ]

            # Sort by problems solved desc, then by total best time asc (fastest), then by total solve time asc, then id
            rows.sort(
                key=lambda r: (
                    -r["solved"],
                    r["total_best_time_ms"],
                    r["total_time_s"],
                    r["student_id"],
                )
            )

            # Assign ranks with ties sharing the same rank key
            leaderboard = []
            rank = 0
            prev_key = None
            for r in rows:
                key = (r["solved"], r["total_best_time_ms"], r["total_time_s"])
                if key != prev_key:
                    rank = len(leaderboard) + 1
                    prev_key = key
                r["rank"] = rank
                leaderboard.append(r)

            return JsonResponse({"leaderboard": leaderboard, "contest": contest.name})

        # No contest provided: aggregate across all
        students_qs = Student.objects.all()
        stats = (
            students_qs.annotate(
                solved_count=Count("solutions", filter=Q(solutions__is_solved=True), distinct=True),
                first_solve=Min("solutions__solved_at", filter=Q(solutions__is_solved=True)),
            )
            .order_by("-solved_count", "first_solve", "id")
            .values("id", "name", "email", "solved_count", "first_solve")
        )

        leaderboard = []
        rank = 0
        prev_key = None
        for row in stats:
            key = (row["solved_count"], row["first_solve"])
            if key != prev_key:
                rank = len(leaderboard) + 1
                prev_key = key
            leaderboard.append(
                {
                    "rank": rank,
                    "student_id": row["id"],
                    "name": row["name"],
                    "email": row["email"],
                    "solved": int(row["solved_count"] or 0),
                    "first_solve_at": row["first_solve"].isoformat()
                    if row["first_solve"]
                    else None,
                    "points": int(row["solved_count"] or 0),
                }
            )

        return JsonResponse({"leaderboard": leaderboard})
    except Exception as e:
        return JsonResponse(
            {
                "error": "Failed to compute leaderboard",
                "details": str(e) if settings.DEBUG else None,
            },
            status=500,
        )
