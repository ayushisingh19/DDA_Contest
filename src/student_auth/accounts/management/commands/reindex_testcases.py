"""
Management command to reindex and fix orphaned testcase files.

This command:
1. Scans the media/testcases directory for uploaded files
2. Finds files that don't have corresponding TestCase database entries
3. Creates missing TestCase entries for valid problem/language combinations
4. Reports on any files that can't be processed
"""

import os
import json
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from accounts.models import Problem, TestCase


class Command(BaseCommand):
    help = "Reindex testcase files and create missing database entries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )
        parser.add_argument(
            "--problem-id",
            type=int,
            help="Only process testcases for a specific problem ID",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        specific_problem = options["problem_id"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )

        media_root = settings.MEDIA_ROOT
        testcases_dir = os.path.join(media_root, "testcases")

        if not os.path.exists(testcases_dir):
            raise CommandError(f"Testcases directory does not exist: {testcases_dir}")

        stats = {
            "problems_processed": 0,
            "files_found": 0,
            "entries_created": 0,
            "entries_existed": 0,
            "files_orphaned": 0,
            "errors": 0,
        }

        self.stdout.write(f"Scanning testcases directory: {testcases_dir}")

        for item in os.listdir(testcases_dir):
            if not item.startswith("problem_"):
                continue

            try:
                problem_id = int(item.replace("problem_", ""))
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f"Invalid problem directory name: {item}")
                )
                stats["errors"] += 1
                continue

            # Skip if specific problem requested
            if specific_problem and problem_id != specific_problem:
                continue

            problem_dir = os.path.join(testcases_dir, item)
            if not os.path.isdir(problem_dir):
                continue

            stats["problems_processed"] += 1
            self.stdout.write(f"\n📁 Processing Problem {problem_id}")

            # Check if problem exists
            try:
                problem = Problem.objects.get(id=problem_id)
                self.stdout.write(f"  ✅ Problem exists: {problem.title}")
            except Problem.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ❌ Problem {problem_id} does not exist in database!"
                    )
                )
                # Count orphaned files
                for file in os.listdir(problem_dir):
                    if file.endswith(".json"):
                        stats["files_orphaned"] += 1
                continue

            # Process files in the problem directory
            for file in os.listdir(problem_dir):
                if not file.endswith(".json"):
                    continue

                stats["files_found"] += 1
                file_path = os.path.join(problem_dir, file)
                # Use forward slashes for cross-platform compatibility with database
                relative_path = f"testcases/{item}/{file}"

                self.stdout.write(f"    📄 Found file: {file}")

                # Extract language from filename
                language = self._extract_language_from_filename(file)
                if not language:
                    self.stdout.write(
                        self.style.ERROR(
                            "      ❌ Could not determine language from filename"
                        )
                    )
                    stats["files_orphaned"] += 1
                    continue

                self.stdout.write(f"      Detected language: {language}")

                # Validate language is supported
                valid_languages = [choice[0] for choice in TestCase.LANGUAGE_CHOICES]
                if language not in valid_languages:
                    self.stdout.write(
                        self.style.ERROR(f"      ❌ Unsupported language: {language}")
                    )
                    self.stdout.write(f"      Valid languages: {valid_languages}")
                    stats["files_orphaned"] += 1
                    continue

                # Check if TestCase entry exists
                existing_testcase = TestCase.objects.filter(
                    problem=problem, language=language, file=relative_path
                ).first()

                if existing_testcase:
                    self.stdout.write(
                        f"      ✅ TestCase entry already exists (ID: {existing_testcase.id})"
                    )
                    stats["entries_existed"] += 1
                    continue

                # Validate file content
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        test_cases = data.get("test_cases", [])
                        if not test_cases:
                            self.stdout.write(
                                self.style.ERROR(
                                    "      ❌ No test_cases found in JSON file"
                                )
                            )
                            stats["files_orphaned"] += 1
                            continue

                        self.stdout.write(
                            f"      ✅ Valid JSON with {len(test_cases)} test cases"
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"      ❌ Invalid JSON file: {e}")
                    )
                    stats["files_orphaned"] += 1
                    continue

                # Create TestCase entry
                if not dry_run:
                    try:
                        testcase = TestCase.objects.create(
                            problem=problem,
                            language=language,
                            file=relative_path,
                            is_hidden=False,  # Default to visible
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"      ✅ Created TestCase entry (ID: {testcase.id})"
                            )
                        )
                        stats["entries_created"] += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"      ❌ Failed to create TestCase: {e}")
                        )
                        stats["errors"] += 1
                else:
                    self.stdout.write("      🔧 Would create TestCase entry (dry run)")
                    stats["entries_created"] += 1

        # Print summary
        self.stdout.write("\n=== Summary ===")
        self.stdout.write(f'Problems processed: {stats["problems_processed"]}')
        self.stdout.write(f'Files found: {stats["files_found"]}')
        self.stdout.write(f'Entries already existed: {stats["entries_existed"]}')
        if dry_run:
            self.stdout.write(f'Entries would be created: {stats["entries_created"]}')
        else:
            self.stdout.write(f'Entries created: {stats["entries_created"]}')
        self.stdout.write(f'Orphaned files: {stats["files_orphaned"]}')
        self.stdout.write(f'Errors: {stats["errors"]}')

        if stats["entries_created"] > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        "\nRun without --dry-run to create the TestCase entries"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Successfully processed {stats["entries_created"]} testcase files'
                    )
                )

    def _extract_language_from_filename(self, filename):
        """
        Extract language from filename patterns like:
        - python_whatever.json -> python
        - cpp_whatever.json -> cpp
        - java_whatever.json -> java
        """
        if not filename.endswith(".json"):
            return None

        # Remove .json extension
        base_name = filename[:-5]

        # Split by underscore and take first part
        parts = base_name.split("_")
        if len(parts) == 0:
            return None

        potential_language = parts[0].lower()

        # Map common variations
        language_map = {
            "py": "python",
            "python3": "python",
            "c++": "cpp",
            "cxx": "cpp",
        }

        return language_map.get(potential_language, potential_language)
