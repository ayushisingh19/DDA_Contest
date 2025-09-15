from django.core.management.base import BaseCommand
from accounts.models import (
    PracticeCategory,
    PracticeSubtopic,
    PracticeQuestion,
    PracticeOption,
)


APT_CAT = "General Aptitude"
VERB_CAT = "Verbal and Reasoning"


class Command(BaseCommand):
    help = "Seed sample aptitude and verbal practice questions"

    def handle(self, *args, **options):
        # Categories
        apt_cat, _ = PracticeCategory.objects.get_or_create(
            slug="general-aptitude", defaults={"name": APT_CAT, "order": 1, "icon": "target"}
        )
        verb_cat, _ = PracticeCategory.objects.get_or_create(
            slug="verbal-reasoning", defaults={"name": VERB_CAT, "order": 2, "icon": "check"}
        )

        # Subtopics
        arithmetic, _ = PracticeSubtopic.objects.get_or_create(category=apt_cat, name="Arithmetic Aptitude", order=1)
        data_int, _ = PracticeSubtopic.objects.get_or_create(category=apt_cat, name="Data Interpretation", order=2)
        verbal_ability, _ = PracticeSubtopic.objects.get_or_create(category=verb_cat, name="Verbal Ability", order=1)
        logical_reasoning, _ = PracticeSubtopic.objects.get_or_create(category=verb_cat, name="Logical Reasoning", order=2)

        # Helper to add question if not exists
        def add_question(subtopic, text, options, correct_index, explanation=""):
            q, created = PracticeQuestion.objects.get_or_create(
                subtopic=subtopic, text=text, defaults={"explanation": explanation}
            )
            if created:
                for i, opt in enumerate(options):
                    PracticeOption.objects.create(
                        question=q, text=opt, is_correct=(i == correct_index), order=i
                    )
                if explanation:
                    q.explanation = explanation
                    q.save()
                self.stdout.write(self.style.SUCCESS(f"Added: {text[:60]}"))
            else:
                self.stdout.write(f"Exists: {text[:60]}")

        # Sample aptitude questions
        add_question(
            arithmetic,
            "If a train travels 120 km in 2 hours, what is its average speed?",
            ["40 km/h", "50 km/h", "60 km/h", "80 km/h"],
            2,
            "Average speed = distance/time = 120/2 = 60 km/h.",
        )

        add_question(
            data_int,
            "A pie chart shows that 25% of a company's 800 employees work in sales. How many is this?",
            ["100", "150", "180", "200"],
            3,
            "25% of 800 = 0.25 * 800 = 200 employees.",
        )

        # Sample verbal questions
        add_question(
            verbal_ability,
            "Choose the synonym for 'CANDID'.",
            ["Secret", "Honest", "Prepared", "Late"],
            1,
            "'Candid' means truthful or honest.",
        )

        add_question(
            logical_reasoning,
            "Find the next number in the series: 2, 6, 12, 20, ?",
            ["28", "30", "32", "34"],
            2,
            "Differences: +4, +6, +8, next +10 -> 20 + 12 = 32.",
        )

        self.stdout.write(self.style.SUCCESS("Seeding complete."))