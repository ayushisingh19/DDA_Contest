# ruff: noqa: E402
import os
from django.core.files.base import ContentFile
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
import django

django.setup()

from accounts.models import Contest, Problem, TestCase


def main():
    contest, _ = Contest.objects.get_or_create(
        name="Practice Contest",
        defaults={
            "start_at": timezone.now(),
            "duration_minutes": 120,
            "is_active": True,
        },
    )

    problem_defaults = {
        "title": "Two Sum",
        "description": (
            "Given an array of integers and a target, return the indices of"
            " two numbers such that they add up to target. Input format: n, then n"
            " integers, then target. Output two 0-based indices separated by space."
        ),
        "difficulty": "Easy",
        "constraints": "1 <= n <= 10^5",
        "function_name": "two_sum",
        "function_params": ["nums", "target"],
        "return_type": "List[int]",
        "default_stub": {
            "python": (
                "# Two Sum — Starter Template\n"
                "# Input format (from stdin):\n"
                "#   n\n"
                "#   n space-separated integers\n"
                "#   target\n"
                "# Output format (to stdout):\n"
                "#   i j   # zero-based indices such that nums[i] + nums[j] == target\n\n"
                "from typing import List, Tuple\n"
                "import sys\n\n"
                "def two_sum(nums: List[int], target: int) -> Tuple[int, int]:\n"
                "    \"\"\"\n"
                "    Return a pair of zero-based indices (i, j) such that:\n"
                "      nums[i] + nums[j] == target and i != j\n"
                "    If no such pair exists, return (-1, -1).\n"
                "    \"\"\"\n"
                "    # TODO: Write your code here\n"
                "    return (-1, -1)  # placeholder; replace with your logic\n\n"
                "def main():\n"
                "    line1 = sys.stdin.readline().strip()\n"
                "    if not line1:\n"
                "        print(\"-1 -1\")\n"
                "        return\n"
                "    n = int(line1)\n"
                "    nums_line = sys.stdin.readline().strip()\n"
                "    nums = list(map(int, nums_line.split())) if nums_line else []\n"
                "    target_line = sys.stdin.readline().strip()\n"
                "    target = int(target_line) if target_line else 0\n\n"
                "    i, j = two_sum(nums, target)\n"
                "    print(f\"{i} {j}\")\n\n"
                "if __name__ == \"__main__\":\n"
                "    main()\n"
            )
        },
    }

    problem, created = Problem.objects.get_or_create(
        contest=contest, code="TWO_SUM", defaults=problem_defaults
    )

    tc_path = os.path.join(
        os.path.dirname(__file__ if "__file__" in globals() else "."),
        "testcases",
        "two_sum_python.json",
    )
    if os.path.exists(tc_path):
        with open(tc_path, "rb") as f:
            content = ContentFile(f.read(), name="two_sum_python.json")
            py_tc, _ = TestCase.objects.get_or_create(
                problem=problem, language="python"
            )
            needs_save = False
            if not py_tc.file or not getattr(py_tc.file, "name", None):
                needs_save = True
            else:
                try:
                    if not os.path.exists(py_tc.file.path):
                        needs_save = True
                except Exception:
                    needs_save = True

            if needs_save:
                py_tc.file.save("two_sum_python.json", content, save=True)
            py_tc.save()
    else:
        print(f"Two Sum testcase not found at {tc_path}")

    print(
        f"Seeded problem: {problem.code} - {problem.title} in contest '{contest.name}'"
    )


if __name__ == "__main__":
    main()
