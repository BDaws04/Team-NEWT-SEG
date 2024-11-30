from django.core.management.base import BaseCommand
from tutorials.models import (
    User, Tutor, Student, Session, StudentSession, ProgrammingLanguage,
    TutorSession, RequestedStudentSession
)

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Removes seeded sample data from the database'

    def handle(self, *args, **options):
        """Unseed the database by removing only non-admin and seeded data."""
        self.stdout.write("Starting to unseed the database...")
        
        # Delete related data first to avoid foreign key constraint violations
        StudentSession.objects.all().delete()
        self.stdout.write("Deleted all StudentSession entries.")
        
        RequestedStudentSession.objects.all().delete()
        self.stdout.write("Deleted all RequestedStudentSession entries.")
        
        TutorSession.objects.all().delete()
        self.stdout.write("Deleted all TutorSession entries.")
        
        ProgrammingLanguage.objects.all().delete()
        
        Session.objects.all().delete()
        self.stdout.write("Deleted all Session entries.")
        
        ProgrammingLanguage.objects.all().delete()
        self.stdout.write("Deleted all ProgrammingLanguage entries.")
        
        Tutor.objects.all().delete()
        self.stdout.write("Deleted all Tutor entries.")
        
        Student.objects.all().delete()
        self.stdout.write("Deleted all Student entries.")
        
        # Delete non-staff users
        User.objects.filter(is_staff=False).delete()
        self.stdout.write("Deleted all non-staff User entries.")

        self.stdout.write("Database unseeding completed.")
