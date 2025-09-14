import pytest
from django.utils import timezone
from accounts.models import (
    Contest,
    Problem,
    Student,
    Submission,
    SubmissionTestCaseResult,
)


@pytest.mark.django_db
def test_weighted_scoring(client):
    contest = Contest.objects.create(name="C1", start_at=timezone.now())
    prob = Problem.objects.create(contest=contest, code="P1", title="T")
    student = Student.objects.create(
        name="A",
        email="a@example.com",
        password="x",
        mobile="",
        college="",
        passout_year=2025,
        branch="",
    )
    sub = Submission.objects.create(
        student=student, problem=prob, code="print(1)", language="python"
    )
    # two testcases: one pass weight 2, one fail weight 1
    SubmissionTestCaseResult.objects.create(
        submission=sub, index=0, group="g1", weight=2, passed=True
    )
    SubmissionTestCaseResult.objects.create(
        submission=sub, index=1, group="g2", weight=1, passed=False
    )
    # emulate aggregation
    total = sum(r.weight for r in sub.results.all())
    gained = sum(r.weight for r in sub.results.all() if r.passed)
    sub.max_score = total
    sub.score = gained
    sub.status = Submission.Status.DONE
    sub.save()
    assert sub.max_score == 3
    assert sub.score == 2
