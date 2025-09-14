# ruff: noqa: E402
#!/usr/bin/env python3
"""
Populate Function Stub Fields for Existing Problems

This script adds function signature metadata to existing problems and generates
default starter code stubs for all supported languages.

Usage:
    python populate_function_stubs.py
"""

import os
import sys

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")
import django

django.setup()

from accounts.models import Problem
from accounts.stub_generator import generate_starter_code


def populate_problem_stubs():
    """Add function signature metadata and generate stubs for existing problems."""

    # Default function signatures for common problem types
    default_signatures = {
        "Sum A+B": {
            "function_name": "add_numbers",
            "function_params": ["a", "b"],
            "return_type": "int",
        },
        "Two Sum": {
            "function_name": "two_sum",
            "function_params": ["nums", "target"],
            "return_type": "List[int]",
        },
        "Palindrome": {
            "function_name": "is_palindrome",
            "function_params": ["s"],
            "return_type": "bool",
        },
        "Reverse String": {
            "function_name": "reverse_string",
            "function_params": ["s"],
            "return_type": "str",
        },
        "Maximum Subarray": {
            "function_name": "max_subarray",
            "function_params": ["nums"],
            "return_type": "int",
        },
    }

    # Languages to generate stubs for
    languages = ["python", "java", "cpp", "csharp", "javascript", "typescript"]

    problems = Problem.objects.all()
    updated_count = 0

    print(f"Found {problems.count()} problems to process...")

    for problem in problems:
        print(f"\nProcessing Problem {problem.id}: {problem.title}")

        # Skip if already has function metadata
        if problem.function_name and problem.function_params:
            print("  ✓ Already has function metadata, skipping...")
            continue

        # Try to match with default signatures
        signature = None
        for title_pattern, sig in default_signatures.items():
            if title_pattern.lower() in problem.title.lower():
                signature = sig
                break

        # Use generic signature if no match found
        if not signature:
            # Extract potential function name from title
            function_name = problem.title.lower().replace(" ", "_").replace("-", "_")
            # Remove non-alphanumeric characters except underscores
            function_name = "".join(c for c in function_name if c.isalnum() or c == "_")
            if not function_name or function_name[0].isdigit():
                function_name = "solution"

            signature = {
                "function_name": function_name,
                "function_params": ["input_data"],  # Generic parameter
                "return_type": "int",
            }

        # Update problem with function metadata
        problem.function_name = signature["function_name"]
        problem.function_params = signature["function_params"]
        problem.return_type = signature["return_type"]

        # Generate default stubs for all languages
        stubs = {}
        for lang in languages:
            try:
                stub = generate_starter_code(lang, problem)
                stubs[lang] = stub
                print(f"  ✓ Generated {lang} stub")
            except Exception as e:
                print(f"  ✗ Failed to generate {lang} stub: {e}")

        # Save stubs to problem
        problem.default_stub = stubs
        problem.save()

        print(f"  ✓ Updated problem with {len(stubs)} language stubs")
        updated_count += 1

    print(
        f"\n🎉 Successfully updated {updated_count} problems with function stub metadata!"
    )
    print("\nSample generated stubs:")

    # Show a sample of generated stubs
    if problems.exists():
        sample_problem = problems.first()
        print(f"\nProblem: {sample_problem.title}")
        print(
            f"Function: {sample_problem.function_name}({', '.join(sample_problem.function_params or [])})"
        )

        for lang in ["python", "java"]:
            if lang in sample_problem.default_stub:
                print(f"\n{lang.upper()} stub:")
                print("─" * 40)
                print(
                    sample_problem.default_stub[lang][:200] + "..."
                    if len(sample_problem.default_stub[lang]) > 200
                    else sample_problem.default_stub[lang]
                )


def main():
    """Main execution function."""
    print("🚀 Populating function stub fields for existing problems...")
    print("=" * 60)

    try:
        populate_problem_stubs()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
