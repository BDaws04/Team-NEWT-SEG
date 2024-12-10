from django.core.management.base import BaseCommand
from tutorials.models import (
    User, Tutor, Student, Session, StudentSession, ProgrammingLanguage,
    TutorSession, RequestedStudentSession
)

class Command(BaseCommand):

    def handle(self, *args, **options):
        StudentSession.objects.all().delete()
        RequestedStudentSession.objects.all().delete()
        TutorSession.objects.all().delete()
        Session.objects.all().delete()
        Student.objects.all().delete()
        Tutor.objects.all().delete()