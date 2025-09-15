from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("healthz/", views.healthz, name="healthz"),
    path("api/healthz/", views.healthz, name="api-healthz"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    # Password Reset URLs
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/<str:token>/", views.reset_password, name="reset_password"),
    path("contest/", views.contest, name="contest"),
    path("contest/junior/", views.contest_junior, name="contest_junior"),
    path("contest/senior/", views.contest_senior, name="contest_senior"),
    # Highlights
    path("highlights/sage/", views.sage_highlights, name="sage_highlights"),
    # Practice
    path("practice/", views.practice_home, name="practice_home"),
    path("practice/question/<int:question_id>/", views.practice_question, name="practice_question"),
    path("practice/subtopic/<int:subtopic_id>/", views.practice_subtopic, name="practice_subtopic"),
    # Admin URLs (staff only)
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("create_contest/", views.create_contest, name="create_contest"),
    path("delete_contest/", views.delete_contest, name="delete_contest"),
    path("evaluate/", views.partial_evaluate, name="evaluate"),
    path("end_contest/", views.end_contest, name="end_contest"),
    # Admin Leaderboards
    path("admin_dashboard/leaderboard/<int:contest_id>/", views.admin_leaderboard, name="admin_leaderboard"),
    path(
    "admin_dashboard/leaderboard/<int:contest_id>/csv/",
        views.admin_leaderboard_csv,
        name="admin_leaderboard_csv",
    ),
    # Problem pages
    path("problems/", views.start, name="problems"),
    path("problems/<int:id>/", views.start, name="problem_detail"),
    path("junior/problems/", views.start_junior, name="junior_problems"),
    path("junior/problems/<int:id>/", views.start_junior, name="junior_problem_detail"),
    path("senior/problems/", views.start_senior, name="senior_problems"),
    path("senior/problems/<int:id>/", views.start_senior, name="senior_problem_detail"),
    # Code execution
    path("run_code/<int:problem_id>/", views.run_code, name="run_code"),
    path(
        "get_visible_testcases/<int:problem_id>/",
        views.get_visible_testcases,
        name="get_visible_testcases",
    ),
    # Async submission APIs
    path("api/submissions/", views.create_submission, name="create_submission"),
    path(
        "api/submissions/<uuid:submission_id>/",
        views.get_submission_status,
        name="submission_status",
    ),
    # Problem APIs
    path(
        "api/problems/",
        views.list_problems,
        name="problem_list_api",
    ),
    path(
        "api/problems/<int:problem_id>/",
        views.get_problem_detail,
        name="problem_detail_api",
    ),
    path(
        "api/problems/<int:problem_id>/starter-code/",
        views.get_starter_code,
        name="starter_code_api",
    ),
    # Leaderboard API
    path("api/leaderboard/", views.leaderboard, name="leaderboard_api"),
    # Health check endpoint
    path("healthz/", views.health_check, name="health_check"),
]
