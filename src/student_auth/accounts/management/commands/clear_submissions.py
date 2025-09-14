from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from accounts.models import Submission, SubmissionTestCaseResult, UserSolution


class Command(BaseCommand):
    help = (
        "Delete Submission records and their related results. "
        "Optionally filter by student, problem, or age. Requires --force to execute."
    )

    def add_arguments(self, parser):
        parser.add_argument("--student-id", type=int, help="Only delete for this student ID")
        parser.add_argument("--problem-id", type=int, help="Only delete for this problem ID")
        parser.add_argument(
            "--older-than-days",
            type=int,
            help="Only delete submissions created more than N days ago",
        )
        parser.add_argument(
            "--status",
            choices=[c for c, _ in Submission.Status.choices],
            help="Only delete submissions with this status",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Execute deletion. Without this flag, the command runs in dry-run mode.",
        )
        parser.add_argument(
            "--reset-solutions",
            action="store_true",
            help=(
                "Also reset UserSolution stats (is_solved, attempts, solved_at, best_*) "
                "for matching student/problem filters."
            ),
        )

    def handle(self, *args, **options):
        qs = Submission.objects.all()

        student_id = options.get("student_id")
        problem_id = options.get("problem_id")
        older_than_days = options.get("older_than_days")
        status = options.get("status")
        force = options.get("force")
        reset_solutions = options.get("reset_solutions")

        if student_id:
            qs = qs.filter(student_id=student_id)
        if problem_id:
            qs = qs.filter(problem_id=problem_id)
        if status:
            qs = qs.filter(status=status)
        if older_than_days is not None:
            cutoff = timezone.now() - timezone.timedelta(days=older_than_days)
            qs = qs.filter(created_at__lt=cutoff)

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No submissions match the given filters."))
            return

        # Count related results for reporting
        result_count = SubmissionTestCaseResult.objects.filter(submission__in=qs).count()

        # If resetting solutions, compute the impacted solution count for reporting
        reset_count = 0
        if reset_solutions:
            sol_qs = UserSolution.objects.all()
            if student_id:
                sol_qs = sol_qs.filter(student_id=student_id)
            if problem_id:
                sol_qs = sol_qs.filter(problem_id=problem_id)
            reset_count = sol_qs.count()

        if not force:
            msg = (
                f"Dry-run: {total} submissions and {result_count} results would be deleted."
            )
            if reset_solutions:
                msg += f" Also would reset {reset_count} solution records."
            msg += " Re-run with --force to apply."
            self.stdout.write(self.style.WARNING(msg))
            return

        # Delete in the right order to avoid large IN queries; results cascade on delete anyway
        # But we count first to report numbers precisely
        deleted, details = qs.delete()
        # Django's delete() cascades and returns a dict with per-model deletions, but here we keep it simple
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {total} submissions and approximately {result_count} related results."
            )
        )

        if reset_solutions:
            sol_qs = UserSolution.objects.all()
            if student_id:
                sol_qs = sol_qs.filter(student_id=student_id)
            if problem_id:
                sol_qs = sol_qs.filter(problem_id=problem_id)
            updated = sol_qs.update(
                is_solved=False,
                attempts=0,
                solved_at=None,
                best_code=None,
                best_time_ms=None,
                best_submission_id=None,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Reset {updated} UserSolution records (is_solved, attempts, solved_at, best_*)."
                )
            )
