from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tutorials.models import User, Tutor, Student, Session, StudentSession, ProgrammingLanguage, TutorSession, RequestedStudentSession
from faker import Faker
from random import choice, randint
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.utils.timezone import make_aware


def calculate_end_date(start_date, duration_weeks):
        return start_date + timedelta(weeks=duration_weeks,days=4)

class Command(BaseCommand):

    TUTOR_COUNT = 5
    STUDENT_COUNT = 5
    SESSION_COUNT = 5
    isPub = True
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker()
        self.User = get_user_model()  # Dynamically get the custom User model

    def handle(self, *args, **options):
        # if(isPub):
        self.create_programming_languages()  
        self.create_tutors_and_students()
        self.seed_sessions()

    def create_programming_languages(self):
        """Populate the ProgrammingLanguage model with common languages."""
        LANGUAGES = [
            'Python', 'Java', 'C++', 'JavaScript', 'Ruby', 'PHP', 'Go', 'Swift', 'Kotlin', 'Rust'
            ]
        for language in LANGUAGES:
            ProgrammingLanguage.objects.create(name=language)

        print("Programming languages seeded.")

    def create_tutors_and_students(self):
        """Create 5 tutors and 5 students with random data."""
        print("Seeding tutors and students...")

        # Create 5 tutors
        for _ in range(self.TUTOR_COUNT):
            self.create_random_tutor()

        # Create 5 students
        for _ in range(self.STUDENT_COUNT):
            self.create_random_student()

    def create_random_tutor(self):
        """Create a random tutor with expertise in programming languages."""
        user = self.User.objects.create_user(
            username='@' + self.faker.unique.user_name(),
            email=self.faker.unique.email(),
            password='Password123',
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
        )
        tutor = Tutor.objects.create(user=user)

        # Assign random programming languages to the tutor
        languages = ProgrammingLanguage.objects.order_by('?')[:randint(1, 4)]
        if languages:
            tutor.expertise.add(*languages)
            print(f"Tutor {user.username} assigned expertise: {[lang.name for lang in languages]}")

    def create_random_student(self):
        """Create a random student."""
        user = self.User.objects.create_user(
            username='@' + self.faker.unique.user_name(),
            email=self.faker.unique.email(),
            password='Password123',
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
        )
        Student.objects.create(user=user)
        print(f"Student {user.username} created.")

    
    def seed_sessions(self):
        """Create sessions with accurate start and end dates based on term start dates."""
        languages = ProgrammingLanguage.objects.all()

        # Updated TERM_START_DATES with Summer starting in May
        TERM_START_DATES = {
            2024: {
                'Fall': datetime(2024, 9, 16),
                'Spring': datetime(2024, 1, 8),
                'Summer': datetime(2024, 5, 6),  # Adjusted to start in May
            },
            2025: {
                'Fall': datetime(2025, 9, 15),
                'Spring': datetime(2025, 1, 6),
                'Summer': datetime(2025, 5, 5),  # Adjusted to start in May
            },
            2026: {
                'Fall': datetime(2026, 9, 14),
                'Spring': datetime(2026, 1, 5),
                'Summer': datetime(2026, 5, 4),  # Adjusted to start in May
            },
        }

        for _ in range(self.SESSION_COUNT):
            language = choice(languages)
            season = choice(['Fall', 'Spring', 'Summer'])
            year = choice(list(TERM_START_DATES.keys()))
            frequency = choice(['Weekly', 'By Weekly'])

            if year not in TERM_START_DATES or season not in TERM_START_DATES[year]:
                print(f"Skipping invalid term configuration for year {year} and season {season}.")
                continue

            start_day = TERM_START_DATES[year][season]
            duration_weeks = 12 if season == 'Fall' else (11 if season == 'Spring' else 6)  # Adjusted durations
            end_day = calculate_end_date(start_day, duration_weeks)

            session = Session.objects.create(
                programming_language=language,
                level=choice(['beginner', 'intermediate', 'advanced']),
                season=season,
                year=year,
                frequency=frequency,
                start_day=start_day,
                end_day=end_day,
                is_available=True
            )

            print(f"Created session for {language.name}, level {session.level}, "
                f"from {start_day} to {end_day}.")

