from django.core.management.base import BaseCommand
from tutorials.models import User, Tutor, Student, Session, StudentSession, ProgrammingLanguage, TutorSession, RequestedStudentSession

class Command(BaseCommand):
    help = 'Unseeds the database by deleting all seeded data'

    def handle(self, *args, **options):
        self.delete_student_sessions()
        self.delete_requested_student_sessions()
        self.delete_tutor_sessions()
        self.delete_sessions()
        self.delete_tutors_and_students()
        self.delete_programming_languages()
        self.delete_required_users()
        print("Database unseeding completed.")

    def delete_student_sessions(self):
        count = StudentSession.objects.count()
        StudentSession.objects.all().delete()
        print(f"Deleted {count} StudentSession records.")

    def delete_requested_student_sessions(self):
        count = RequestedStudentSession.objects.count()
        RequestedStudentSession.objects.all().delete()
        print(f"Deleted {count} RequestedStudentSession records.")

    def delete_tutor_sessions(self):
        count = TutorSession.objects.count()
        TutorSession.objects.all().delete()
        print(f"Deleted {count} TutorSession records.")

    def delete_sessions(self):
        count = Session.objects.count()
        Session.objects.all().delete()
        print(f"Deleted {count} Session records.")

    def delete_tutors_and_students(self):
        # Delete tutors
        tutor_count = Tutor.objects.count()
        Tutor.objects.all().delete()
        print(f"Deleted {tutor_count} Tutor records.")

        # Delete students
        student_count = Student.objects.count()
        Student.objects.all().delete()
        print(f"Deleted {student_count} Student records.")

        # Delete associated users
        tutor_and_student_users = User.objects.filter(role__in=[User.Roles.TUTOR, User.Roles.STUDENT]).count()
        User.objects.filter(role__in=[User.Roles.TUTOR, User.Roles.STUDENT]).delete()
        print(f"Deleted {tutor_and_student_users} User records (TUTORS and STUDENTS).")

    def delete_programming_languages(self):
        count = ProgrammingLanguage.objects.count()
        ProgrammingLanguage.objects.all().delete()
        print(f"Deleted {count} ProgrammingLanguage records.")

    def delete_required_users(self):
        required_users = ['@johndoe', '@janedoe', '@charlie']
        deleted_count = User.objects.filter(username__in=required_users).delete()[0]
        print(f"Deleted {deleted_count} required user accounts ({', '.join(required_users)}).")
