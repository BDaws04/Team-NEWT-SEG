from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tutorials.models import User, Admin, Tutor, Student, Session, StudentSession, ProgrammingLanguage
from faker import Faker
from random import choice, randint
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.utils.timezone import make_aware


class Command(BaseCommand):
    """Database seeder for creating users, tutors, students, and courses."""

    USER_COUNT = 300
    NUM_SESSIONS = 100
    NUM_STUDENT_SESSIONS = 50
    DEFAULT_PASSWORD = 'Password123'
    LANGUAGES = [
        'Python', 'Java', 'C++', 'JavaScript', 'Ruby', 'PHP', 'Go', 'Swift', 'Kotlin', 'Rust'
    ]
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker()
        self.User = get_user_model()  # Dynamically get the custom User model

    def handle(self, *args, **options):
        self.create_programming_languages()  # Populate ProgrammingLanguage first
        self.create_users()
        self.create_tutors_and_students()
        self.seed_sessions()
        self.seed_student_sessions()

    def create_programming_languages(self):
        """Seed predefined programming languages."""
        for language in self.LANGUAGES:
            ProgrammingLanguage.objects.get_or_create(name=language)
        print("Programming languages seeded.")

    def seed_sessions(self):
        tutors = Tutor.objects.prefetch_related("expertise").all()
        current_year = datetime.now().year
        available_years = [current_year, current_year + 1, current_year + 2]  # Example years

        for _ in range(self.NUM_SESSIONS):
            tutor = choice(tutors)

            expertise_languages = list(tutor.expertise.all())
            if not expertise_languages:
                print(f"Skipping tutor {tutor.user.username} (no expertise assigned).")
                continue

            language = choice(expertise_languages)
            print(f"Assigning programming language {language.name} to session for tutor {tutor.user.username}.")

            season = choice(['Fall', 'Spring', 'Summer'])
            year = choice(available_years)

            start_time = make_aware(datetime.now() + timedelta(days=randint(1, 30), hours=randint(8, 20)))
            end_time = start_time + timedelta(hours=2)

            Session.objects.create(
                programming_language=language,
                tutor=tutor,
                level=choice(['beginner', 'intermediate', 'advanced']),
                season=season,
                year=year,
                start_time=start_time,
                end_time=end_time,
            )

        print(f"{self.NUM_SESSIONS} sessions seeded.")


    def seed_student_sessions(self):
        """Link students to sessions."""
        students = Student.objects.all()
        sessions = Session.objects.all()

        for _ in range(self.NUM_STUDENT_SESSIONS):
            student = choice(students)
            session = choice(sessions)

            StudentSession.objects.get_or_create(student=student, session=session)

        print(f"{self.NUM_STUDENT_SESSIONS} student sessions seeded.")

    def create_users(self):
        """Create specific user roles."""
        self.create_admin_user()
        self.create_tutor_user()
        self.create_student_user()

    def create_admin_user(self):
        """Create an admin user."""
        admin_user = self.User.objects.create_superuser(
            username='@johndoe',
            email='john.doe@example.org',
            password=self.DEFAULT_PASSWORD,
            first_name='John',
            last_name='Doe',
        )
        Admin.objects.create(user=admin_user, admin_level='senior')
        print("Admin user created.")

    def create_tutor_user(self):
        user = self.User.objects.create_user(
            username='@' + self.faker.unique.user_name(),
            email=self.faker.unique.email(),
            password=self.DEFAULT_PASSWORD,
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
        )
        tutor = Tutor.objects.create(
            user=user,
            hourly_rate=randint(20, 100),
        )
        languages = ProgrammingLanguage.objects.order_by('?')[:randint(1, 4)]
        if not languages:
            print(f"No programming languages available to assign to tutor {user.username}.")
        else:
            tutor.expertise.add(*languages)

    def create_student_user(self):
        """Create a student user."""
        student_user = self.User.objects.create_user(
            username='@charlie',
            email='charlie.johnson@example.org',
            password=self.DEFAULT_PASSWORD,
            first_name='Charlie',
            last_name='Johnson',
        )
        student = Student.objects.create(user=student_user)
        print("Student user created.")

    def create_tutors_and_students(self):
        """Generate random tutors and students."""
        print("Seeding random users...")
        for _ in range(self.USER_COUNT // 2):
            self.create_random_tutor()

        for _ in range(self.USER_COUNT // 2):
            self.create_random_student()

    def create_random_tutor(self):
        user = self.User.objects.create_user(
            username='@' + self.faker.unique.user_name(),
            email=self.faker.unique.email(),
            password=self.DEFAULT_PASSWORD,
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
        )
        tutor = Tutor.objects.create(
            user=user,
            hourly_rate=randint(20, 100),
        )

        # Assign random programming languages
        languages = ProgrammingLanguage.objects.order_by('?')[:randint(1, 4)]
        if not languages:
            print(f"No programming languages available to assign to tutor {user.username}.")
        else:
            tutor.expertise.add(*languages)
            print(f"Tutor {user.username} assigned expertise: {[lang.name for lang in languages]}")

    def create_random_student(self):
        user = self.User.objects.create_user(
            username='@' + self.faker.unique.user_name(),
            email=self.faker.unique.email(),
            password=self.DEFAULT_PASSWORD,
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
        )
        Student.objects.create(user=user)

    


        

