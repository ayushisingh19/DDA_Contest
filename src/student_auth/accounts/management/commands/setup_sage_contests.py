import os
import glob
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from accounts.models import Contest, Problem, TestCase


class Command(BaseCommand):
    help = "Create Junior and Senior contests; import provided Junior problems and testcases"

    def add_arguments(self, parser):
        parser.add_argument(
            "--base",
            default=os.path.join(
                settings.MEDIA_ROOT, "testcases", "SAGE Junior Contest"
            ),
            help="Base folder containing the Junior problems (defaults to media/testcases/SAGE Junior Contest)",
        )
        parser.add_argument(
            "--junior-name",
            default="SAGE Junior Contest",
            help="Name of the Junior contest",
        )
        parser.add_argument(
            "--senior-name",
            default="SAGE Senior Contest",
            help="Name of the Senior contest",
        )

    def handle(self, *args, **opts):
        base_dir = opts["base"]
        # argparse converts dashes to underscores
        junior_name = opts.get("junior_name") or opts.get("junior-name") or "SAGE Junior Contest"
        senior_name = opts.get("senior_name") or opts.get("senior-name") or "SAGE Senior Contest"

        if not os.path.isdir(base_dir):
            self.stderr.write(self.style.ERROR(f"Base directory not found: {base_dir}"))
            return

        junior, _ = Contest.objects.get_or_create(
            name=junior_name,
            defaults={
                "start_at": timezone.now(),
                "duration_minutes": 60,
                "is_active": True,
            },
        )
        senior, _ = Contest.objects.get_or_create(
            name=senior_name,
            defaults={
                "start_at": timezone.now(),
                "duration_minutes": 60,
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS(f"Ensured contests: {junior.name}, {senior.name}"))

        # Collect problem folders under base_dir
        problem_dirs = [p for p in glob.glob(os.path.join(base_dir, "*")) if os.path.isdir(p)]
        problem_dirs.sort()

        for idx, pdir in enumerate(problem_dirs, start=1):
            folder = os.path.basename(pdir)
            title = folder.replace("_", " ").replace("-", " ").title()
            code = f"P{idx}"

            problem, created = Problem.objects.get_or_create(
                contest=junior,
                code=code,
                defaults={
                    "title": title,
                    "difficulty": "Easy",
                },
            )
            if created:
                # Optional description.txt
                desc_path = os.path.join(pdir, "description.txt")
                if os.path.exists(desc_path):
                    try:
                        with open(desc_path, "r", encoding="utf-8") as fh:
                            problem.description = fh.read().strip()
                    except Exception:
                        pass
                # Optional starter templates
                tpl_dir = os.path.join(pdir, "template")
                default_stub = {}
                py_tpl = os.path.join(tpl_dir, f"{folder}_template.py")
                cpp_tpl = os.path.join(tpl_dir, f"{folder}_template.cpp")
                if os.path.exists(py_tpl):
                    try:
                        with open(py_tpl, "r", encoding="utf-8") as fh:
                            default_stub["python"] = fh.read()
                    except Exception:
                        pass
                if os.path.exists(cpp_tpl):
                    try:
                        with open(cpp_tpl, "r", encoding="utf-8") as fh:
                            default_stub["cpp"] = fh.read()
                    except Exception:
                        pass
                if default_stub:
                    problem.default_stub = default_stub
                problem.save()

            # Create/attach testcases (python & cpp) pointing to existing files under MEDIA_ROOT
            for lang in ("python", "cpp"):
                pattern = os.path.join(pdir, f"*_{lang}_testcases.json")
                for fpath in glob.glob(pattern):
                    rel = os.path.relpath(fpath, settings.MEDIA_ROOT)
                    # Ensure clean posix-like path for FileField storage
                    rel = rel.replace("\\", "/")
                    # Check if a TestCase already exists pointing to this language
                    tc, _ = TestCase.objects.get_or_create(
                        problem=problem, language=lang
                    )
                    # Assign file name to reference existing file in MEDIA_ROOT
                    tc.file.name = rel
                    tc.is_hidden = False
                    tc.save()
                    self.stdout.write(f"Linked {lang} testcases for {problem.code} -> {rel}")

        self.stdout.write(self.style.SUCCESS("Junior contest problems imported. Senior contest left empty as requested."))
