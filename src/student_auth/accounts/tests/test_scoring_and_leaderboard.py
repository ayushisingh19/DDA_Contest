import json
import os
import shutil
import tempfile
from datetime import timedelta

from django.test import TestCase, override_settings, Client
from django.core.files.base import ContentFile
from django.utils import timezone
from unittest.mock import patch

from accounts.models import Contest, Problem, TestCase as TCModel, Student, Submission, UserSolution
from accounts.tasks import evaluate_submission, _post_evaluation_update


def make_testcase_file(problem: Problem, language: str, cases):
    data = {"test_cases": cases}
    content = ContentFile(json.dumps(data).encode("utf-8"))
    tc = TCModel.objects.create(problem=problem, language=language)
    tc.file.save("cases.json", content, save=True)
    return tc


@override_settings(DEBUG=True)
class ScoringAndLeaderboardTests(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="media_")
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir, ignore_errors=True))
        self.client = Client()

    def _create_basic_contest_problem(self):
        start = timezone.now() - timedelta(minutes=10)
        contest = Contest.objects.create(
            name="UnitTest Contest",
            start_at=start,
            duration_minutes=120,
            is_active=True,
        )
        problem = Problem.objects.create(
            contest=contest,
            code="P1",
            title="Echo 42",
            description="Print 42 regardless of input",
        )
        return contest, problem

    @override_settings(MEDIA_ROOT="/tmp/test_media_scoring")
    @patch("accounts.tasks._check_judge0_connectivity", return_value=(False, "forced"))
    def test_submission_scoring_full_pass_and_usersolution_update(self, _mock_j0):
        contest, problem = self._create_basic_contest_problem()

        # Two identical tests so code can pass both with same output
        make_testcase_file(
            problem,
            "python",
            [
                {"test_case_no": 1, "stdin": "", "expected_output": "42", "weight": 1},
                {"test_case_no": 2, "stdin": "", "expected_output": "42", "weight": 1},
            ],
        )

        student = Student.objects.create(
            name="Alice", email="alice@example.com", password="x", mobile="1", college="c", passout_year=2025, branch="CS"
        )

        # Code that prints 42
        code = "print(42)\n"
        sub = Submission.objects.create(student=student, problem=problem, code=code, language="python")

        # Run task synchronously (local fallback forced)
        res = evaluate_submission.apply(args=[str(sub.id)])
        self.assertEqual(res.result, str(sub.id))

        sub.refresh_from_db()
        self.assertEqual(sub.status, Submission.Status.DONE)
        self.assertEqual(sub.max_score, 2.0)
        self.assertEqual(sub.score, 2.0)
        self.assertEqual(sub.results.count(), 2)
        self.assertTrue(all(r.passed for r in sub.results.all()))

        us = UserSolution.objects.get(student=student, problem=problem)
        self.assertTrue(us.is_solved)
        self.assertIsNotNone(us.solved_at)
        # Local executor returns 100ms per test => total 200ms
        self.assertAlmostEqual(us.best_time_ms or 0.0, 200.0, places=3)

    @override_settings(MEDIA_ROOT="/tmp/test_media_fastest")
    @patch("accounts.tasks._check_judge0_connectivity", return_value=(False, "forced"))
    def test_fastest_time_updates_when_better_submission_occurs(self, _mock_j0):
        contest, problem = self._create_basic_contest_problem()
        make_testcase_file(
            problem,
            "python",
            [
                {"stdin": "", "expected_output": "OK", "weight": 1},
                {"stdin": "", "expected_output": "OK", "weight": 1},
            ],
        )
        student = Student.objects.create(
            name="Bob", email="bob@example.com", password="x", mobile="1", college="c", passout_year=2025, branch="CS"
        )

        code_ok = "print('OK')\n"
        sub1 = Submission.objects.create(student=student, problem=problem, code=code_ok, language="python")
        evaluate_submission.apply(args=[str(sub1.id)])
        us = UserSolution.objects.get(student=student, problem=problem)
        self.assertAlmostEqual(us.best_time_ms or 0.0, 200.0, places=3)

        # Create a synthetic faster submission: 2 testcases, 50ms each => 100ms total
        sub2 = Submission.objects.create(student=student, problem=problem, code=code_ok, language="python")
        # Mark as evaluated with full score
        sub2.status = Submission.Status.DONE
        sub2.max_score = 2
        sub2.score = 2
        sub2.save()
        # Create results with lower times
        from accounts.models import SubmissionTestCaseResult

        SubmissionTestCaseResult.objects.create(
            submission=sub2, index=0, group="g", weight=1.0, passed=True, status="Accepted", time_ms=50.0
        )
        SubmissionTestCaseResult.objects.create(
            submission=sub2, index=1, group="g", weight=1.0, passed=True, status="Accepted", time_ms=50.0
        )

        # Trigger post-evaluation updates
        _post_evaluation_update(sub2)

        us.refresh_from_db()
        self.assertAlmostEqual(us.best_time_ms or 0.0, 100.0, places=3)
        self.assertEqual(us.best_submission_id, sub2.id)

    @override_settings(MEDIA_ROOT="/tmp/test_media_leaderboard")
    def test_leaderboard_global_by_solved(self):
        # Three students with different solved counts
        s1 = Student.objects.create(name="S1", email="s1@example.com", password="x", mobile="1", college="c", passout_year=2025, branch="CS")
        s2 = Student.objects.create(name="S2", email="s2@example.com", password="x", mobile="1", college="c", passout_year=2025, branch="CS")
        s3 = Student.objects.create(name="S3", email="s3@example.com", password="x", mobile="1", college="c", passout_year=2025, branch="CS")

        start = timezone.now() - timedelta(minutes=60)
        contest = Contest.objects.create(name="LB Global", start_at=start, duration_minutes=180)
        p1 = Problem.objects.create(contest=contest, code="A", title="A")
        p2 = Problem.objects.create(contest=contest, code="B", title="B")

        # Mark solutions manually
        UserSolution.objects.create(student=s1, problem=p1, is_solved=True, solved_at=start + timedelta(minutes=10))
        UserSolution.objects.create(student=s1, problem=p2, is_solved=True, solved_at=start + timedelta(minutes=20))

        UserSolution.objects.create(student=s2, problem=p1, is_solved=True, solved_at=start + timedelta(minutes=15))

        # s3 has 0 solved

        resp = self.client.get("/api/leaderboard/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["leaderboard"]
        # Expect order: s1 (2), s2 (1), s3 (0)
        ids = [row["student_id"] for row in data]
        self.assertEqual(ids, [s1.id, s2.id, s3.id])

    @override_settings(MEDIA_ROOT="/tmp/test_media_leaderboard_contest")
    def test_leaderboard_contest_uses_fastest_time_tie_break(self):
        start = timezone.now() - timedelta(minutes=30)
        contest = Contest.objects.create(name="LB Contest", start_at=start, duration_minutes=120)
        p = Problem.objects.create(contest=contest, code="X", title="X")

        a = Student.objects.create(name="A", email="a@example.com", password="x", mobile="1", college="c", passout_year=2025, branch="CS")
        b = Student.objects.create(name="B", email="b@example.com", password="x", mobile="1", college="c", passout_year=2025, branch="CS")

        ua = UserSolution.objects.create(student=a, problem=p, is_solved=True, solved_at=start + timedelta(minutes=5), best_time_ms=300.0)
        ub = UserSolution.objects.create(student=b, problem=p, is_solved=True, solved_at=start + timedelta(minutes=6), best_time_ms=200.0)

        # Both solved 1; b is faster (200ms < 300ms), should rank above a
        resp = self.client.get(f"/api/leaderboard/?contest_id={contest.id}")
        self.assertEqual(resp.status_code, 200)
        rows = resp.json()["leaderboard"]
        names = [r["name"] for r in rows]
        self.assertEqual(names[0], "B")
        self.assertEqual(names[1], "A")

    @override_settings(MEDIA_ROOT="/tmp/test_media_wrong")
    @patch("accounts.tasks._check_judge0_connectivity", return_value=(False, "forced"))
    def test_submission_scoring_partial_or_wrong(self, _mock_j0):
        contest, problem = self._create_basic_contest_problem()
        make_testcase_file(
            problem,
            "python",
            [
                {"stdin": "", "expected_output": "OK", "weight": 1},
                {"stdin": "", "expected_output": "OK", "weight": 1},
            ],
        )
        student = Student.objects.create(
            name="Eve", email="eve@example.com", password="x", mobile="1", college="c", passout_year=2025, branch="CS"
        )

        # Wrong code: prints something else
        code_bad = "print('NOPE')\n"
        sub = Submission.objects.create(student=student, problem=problem, code=code_bad, language="python")
        evaluate_submission.apply(args=[str(sub.id)])
        sub.refresh_from_db()
        self.assertEqual(sub.status, Submission.Status.DONE)
        self.assertEqual(sub.max_score, 2.0)
        self.assertEqual(sub.score, 0.0)

        # Ensure not marked as solved
        self.assertFalse(UserSolution.objects.filter(student=student, problem=problem, is_solved=True).exists())
