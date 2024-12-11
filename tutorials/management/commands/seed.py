from django.core.management.base import BaseCommand
from tutorials.models import User, Tutor, Student, Session, StudentSession, ProgrammingLanguage, TutorSession, RequestedStudentSession
from faker import Faker
from random import choice, randint
from django.utils.timezone import now
from datetime import datetime, timedelta


def calculate_end_date(start_date, duration_weeks):
    return start_date + timedelta(weeks=duration_weeks, days=4)


class Command(BaseCommand):
    STUDENT_COUNT = 300
    TUTOR_COUNT = 150
    TUTOR_SESSION_COUNT = 300
    REQ_STUDENT_SESSION_COUNT = 200
    PASSWORD = 'Password123'

    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker()

    def handle(self, *args, **options):

        StudentSession.objects.all().delete()
        RequestedStudentSession.objects.all().delete()
        TutorSession.objects.all().delete()
        Session.objects.all().delete()
        Student.objects.all().delete()
        Tutor.objects.all().delete()

        # self.create_required_users()
        self.create_programming_languages()
        self.seed_sessions()
        self.create_tutors_and_students()
        self.create_tutor_sessions()
        self.create_requested_student_sessions() 
        self.create_student_sessions()
        
    def create_programming_languages(self):
        LANGUAGES = [
            'Python', 'Java', 'C++', 'JavaScript', 'Ruby', 'PHP', 'Go', 'Swift', 'Kotlin', 'Rust'
        ]
        for language in LANGUAGES:
            ProgrammingLanguage.objects.create(name=language)

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
        TERM_START_DATES = {
            2024: {
                'Fall': datetime(2024, 9, 16),
                'Spring': datetime(2024, 1, 8),
                'Summer': datetime(2024, 5, 6),
            },
            2025: {
                'Fall': datetime(2025, 9, 15),
                'Spring': datetime(2025, 1, 6),
                'Summer': datetime(2025, 5, 5),
            },
            2026: {
                'Fall': datetime(2026, 9, 14),
                'Spring': datetime(2026, 1, 5),
                'Summer': datetime(2026, 5, 4),
            },
        }
        frequencies = ['Weekly', 'Bi-Weekly']
        levels = ['beginner', 'intermediate', 'advanced']
        programming_languages = ProgrammingLanguage.objects.all()

        for year, seasons in TERM_START_DATES.items():
            for season, start_date in seasons.items():
                for language in programming_languages:
                    for frequency in frequencies:
                        for level in levels:
                            duration_weeks = 12 if season == 'Fall' else (11 if season == 'Spring' else 6)
                            end_date = calculate_end_date(start_date, duration_weeks)
                            Session.objects.create(
                                programming_language=language,
                                level=level,
                                season=season,
                                year=year,
                                frequency=frequency,
                                start_day=start_date,
                                end_day=end_date,
                                is_available=True,
                            )
        print("Sessions seeded.")

    def create_tutors_and_students(self):
        print("Creating tutors and students...")

        for _ in range(self.TUTOR_COUNT):
            user = User.objects.create_user(
                username='@' + self.faker.unique.user_name(),
                email=self.faker.unique.email(),
                password=self.PASSWORD,
                first_name=self.faker.first_name(),
                last_name=self.faker.last_name(),
                role=User.Roles.TUTOR,
            )
            tutor = Tutor.objects.create(user=user)
            languages = ProgrammingLanguage.objects.order_by('?')[:randint(1, 4)]
            tutor.expertise.set(languages)
            # print(f"Tutor {user.username} created with expertise: {[lang.name for lang in languages]}.")

        for _ in range(self.STUDENT_COUNT):
            user = User.objects.create_user(
                username='@' + self.faker.unique.user_name(),
                email=self.faker.unique.email(),
                password=self.PASSWORD,
                first_name=self.faker.first_name(),
                last_name=self.faker.last_name(),
                role=User.Roles.STUDENT,
            )
            Student.objects.create(user=user)
            print(f"Student {user.username} created.")

    def create_tutor_sessions(self):
        tutors = Tutor.objects.prefetch_related('expertise').all()
        sessions = Session.objects.all()

        for _ in range(self.TUTOR_SESSION_COUNT):
            tutor = choice(tutors)
            eligible_sessions = sessions.filter(programming_language__in=tutor.expertise.all())
            if not eligible_sessions.exists():
                continue
            session = choice(eligible_sessions)
            TutorSession.objects.create(tutor=tutor, session=session)
            # print(f"TutorSession created for tutor {tutor.user.username} and session {session.programming_language.name}.")

    def create_requested_student_sessions(self):
        students = Student.objects.all()
        sessions = Session.objects.all()

        for _ in range(self.REQ_STUDENT_SESSION_COUNT):  
            student = choice(students)
            session = choice(sessions)

            
            if RequestedStudentSession.objects.filter(student=student, session=session).exists():
                continue

           
            requested_session = RequestedStudentSession.objects.create(
                student=student,
                session=session,
            )

           
            eligible_tutor_sessions = TutorSession.objects.filter(
                session__programming_language=session.programming_language,
                session__level=session.level,
                session__season=session.season,
                session__year=session.year,
            )
            requested_session.available_tutor_sessions.set(eligible_tutor_sessions)

            # print(f"RequestedStudentSession created for student {student.user.username} and session {session.programming_language.name}.")


    def create_student_sessions(self):
        print("Creating student sessions...")
        requested_sessions = RequestedStudentSession.objects.filter(is_approved=False).prefetch_related(
            'available_tutor_sessions', 'student', 'session'
        )

        for requested_session in requested_sessions:
            available_tutor_sessions = requested_session.available_tutor_sessions.all()

            if not available_tutor_sessions.exists():
                print(f"No available tutor sessions for requested session: {requested_session}")
                continue

            tutor_session = choice(available_tutor_sessions)

            if not tutor_session.session.is_available:
                print(f"Session {tutor_session.session} is unavailable for tutor {tutor_session.tutor.user.username}. Skipping.")
                continue

            if StudentSession.objects.filter(
                student=requested_session.student,
                tutor_session__session__programming_language=requested_session.session.programming_language,
                tutor_session__session__year=requested_session.session.year,
                tutor_session__session__season=requested_session.session.season,
            ).exists():
                print(f"Student {requested_session.student.user.username} is already enrolled in a similar session.")
                continue

            student_session = StudentSession.objects.create(
                student=requested_session.student,
                tutor_session=tutor_session
            )

            tutor_session.session.is_available = False
            tutor_session.session.save()

            tutor_session.delete()
            requested_session.delete()

    def create_required_users(self):
        if not User.objects.filter(username="@johndoe").exists():
            admin_user = User.objects.create_user(
                username="@johndoe",
                email="johndoe@example.com",
                password=self.PASSWORD,
                first_name="John",
                last_name="Doe",
                role=User.Roles.ADMIN,
            )
            print("Admin user @johndoe created.")
        
        if not User.objects.filter(username="@janedoe").exists():
            tutor_user = User.objects.create_user(
                username="@janedoe",
                email="janedoe@example.com",
                password=self.PASSWORD,
                first_name="Jane",
                last_name="Doe",
                role=User.Roles.TUTOR,
            )
            tutor = Tutor.objects.create(user=tutor_user)
            programming_languages = ProgrammingLanguage.objects.order_by('?')[:3]
            tutor.expertise.set(programming_languages)
            print(f"Tutor @janedoe created with expertise: {[lang.name for lang in programming_languages]}")
        
        if not User.objects.filter(username="@charlie").exists():
            student_user = User.objects.create_user(
                username="@charlie",
                email="charlie@example.com",
                password=self.PASSWORD,
                first_name="Charlie",
                last_name="Brown",
                role=User.Roles.STUDENT,
            )
            student = Student.objects.create(user=student_user)
            print("Student user @charlie created.")
            
                





    # def create_student_sessions(self):
    #     students = Student.objects.all()
    #     tutor_sessions = TutorSession.objects.all()

    #     # Create requested student sessions
    #     for _ in range(self.STUDENT_SESSION_COUNT):
    #         student = choice(students)
    #         session = choice(Session.objects.all())

    #         # Ensure no duplicate requests for the same language, year, and term
    #         if RequestedStudentSession.objects.filter(
    #             student=student,
    #             session__programming_language=session.programming_language,
    #             session__year=session.year,
    #             session__season=session.season
    #         ).exists():
    #             continue

    #         requested_session = RequestedStudentSession.objects.create(
    #             student=student,
    #             session=session,
    #         )

    #         # Assign eligible tutor sessions to the request
    #         eligible_tutor_sessions = tutor_sessions.filter(session=session)
    #         if eligible_tutor_sessions.exists():
    #             requested_session.available_tutor_sessions.set(eligible_tutor_sessions)

    #         print(f"RequestedStudentSession created for {student.user.username} and session {session.programming_language.name}.")

    #     # Approve requested sessions
    #     for _ in range(self.APPROVED_SESSION_COUNT):
    #         student = choice(students)
    #         matching_requests = RequestedStudentSession.objects.filter(
    #             student=student,
    #             is_approved=False
    #         ).select_related('session').prefetch_related('available_tutor_sessions')

    #         if not matching_requests.exists():
    #             continue

    #         requested_session = choice(matching_requests)
    #         eligible_tutor_sessions = requested_session.available_tutor_sessions.all()

    #         if not eligible_tutor_sessions.exists():
    #             continue

    #         tutor_session = choice(eligible_tutor_sessions)

    #         # Check if the student is already enrolled in the same language, year, and term
    #         if StudentSession.objects.filter(
    #             student=student,
    #             tutor_session__session__programming_language=requested_session.session.programming_language,
    #             tutor_session__session__year=requested_session.session.year,
    #             tutor_session__session__season=requested_session.session.season
    #         ).exists():
    #             continue

    #         # Approve the session
    #         StudentSession.objects.create(student=student, tutor_session=tutor_session)
    #         requested_session.is_approved = True
    #         requested_session.save()

    #         print(f"Approved session created for {student.user.username} and tutor {tutor_session.tutor.user.username}.")
