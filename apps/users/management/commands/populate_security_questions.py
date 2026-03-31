from django.core.management.base import BaseCommand
from apps.users.models import SecurityQuestion


class Command(BaseCommand):
    help = "Populate default security questions for password recovery"

    def handle(self, *args, **options):
        questions_data = [
            ("What is your favorite dog breed?", "pet"),
            ("What is your favorite food?", "food"),
            ("What is your favorite travel destination?", "travel"),
            ("What is your mother's maiden name?", "personal"),
            ("In what city were you born?", "personal"),
            ("What is the name of your first pet?", "pet"),
            ("What is your favorite movie?", "personal"),
            ("What is your favorite book?", "personal"),
            ("What is your favorite color?", "personal"),
            ("What is the name of the street you grew up on?", "personal"),
            ("What is your favorite cuisine?", "food"),
            ("What is your favorite sport?", "personal"),
            ("What is your all-time favorite band or artist?", "personal"),
            ("What country would you most like to visit?", "travel"),
            ("What is your favorite hobby?", "personal"),
        ]

        created = 0
        for question_text, category in questions_data:
            question, created_flag = SecurityQuestion.objects.get_or_create(
                question=question_text,
                defaults={"category": category}
            )
            if created_flag:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: "{question_text}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⟳ Already exists: "{question_text}"')
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Total: {created} new questions added")
        )
