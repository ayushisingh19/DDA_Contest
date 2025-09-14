import os
import sys
import time
import django


def _bootstrap_django() -> None:
    """Configure sys.path and initialize Django before importing models/tasks."""
    # Ensure the parent of this script (src/student_auth) is on sys.path
    base_dir = os.path.dirname(__file__)
    parent = os.path.abspath(os.path.join(base_dir, os.pardir))
    if parent not in sys.path:
        sys.path.append(parent)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
    django.setup()


def main():
    _bootstrap_django()
    # Local imports after Django setup
    from accounts.models import Problem, Submission
    from accounts.tasks import evaluate_submission

    # Ensure TWO_SUM problem exists
    try:
        problem = Problem.objects.get(code="TWO_SUM")
    except Problem.DoesNotExist:
        print("TWO_SUM problem not found. Seed it first.")
        return

    # Minimal correct Python solution respecting the testcase I/O
    code = (
        "import sys\n"
        "n=int(sys.stdin.readline().strip())\n"
        "nums=list(map(int,sys.stdin.readline().split()))\n"
        "target=int(sys.stdin.readline().strip())\n"
        "s={}\n"
        "for i,v in enumerate(nums):\n"
        "    need=target-v\n"
        "    if need in s:\n"
        "        print(s[need], i)\n"
        "        break\n"
        "    s[v]=i\n"
    )

    sub = Submission.objects.create(problem=problem, code=code, language="python")
    print("Created submission:", sub.id)

    # Queue evaluation
    evaluate_submission.delay(str(sub.id))

    # Poll for up to 60 seconds
    for i in range(60):
        sub.refresh_from_db()
        print(f"[{i:02d}s] status={sub.status} score={sub.score}/{sub.max_score}")
        if sub.status in (Submission.Status.DONE, Submission.Status.ERROR):
            break
        time.sleep(1)

    # Print summary
    print("Final:", sub.status, sub.score, "/", sub.max_score)
    if sub.judge0_raw:
        print("judge0_raw keys:", list(sub.judge0_raw.keys()))


if __name__ == "__main__":
    main()
