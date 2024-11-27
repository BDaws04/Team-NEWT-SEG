from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.utils.timezone import now
from datetime import datetime, timedelta

def default_end_time():
    return now() + timedelta(hours=2)

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STUDENT = 'STUDENT', 'Student'
        TUTOR = 'TUTOR', 'Tutor'

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.STUDENT,
        blank=False
    )

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""
        return f'{self.first_name} {self.last_name}'
    
    def roll(self):
        """Return a string containing the user's role."""

        return self.role

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    previous_sessions = models.ManyToManyField('Session', related_name='students_taken', blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f'Student: {self.user.get_full_name()}'

class ProgrammingLanguage(models.Model):
    LANGUAGES = [
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('C++', 'C++'),
        ('JavaScript', 'JavaScript'),
        ('Ruby', 'Ruby'),
        ('PHP', 'PHP'),
        ('Go', 'Go'),
        ('Swift', 'Swift'),
        ('Kotlin', 'Kotlin'),
        ('Rust', 'Rust'),
    ]

    name = models.CharField(
        max_length=50,
        unique=True,
        choices=LANGUAGES,
        help_text="Select a programming language"
    )

    def __str__(self):
        return self.name

class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tutor_profile")
    expertise = models.ManyToManyField(
        ProgrammingLanguage,
        related_name='tutors',
        blank=True,
        help_text="Select programming languages the tutor can teach"
    )

    def expertise_list(self):
        return ', '.join([language.name for language in self.expertise.all()])

    expertise_list.short_description = 'Expertise'

    def __str__(self):
        return f'Tutor: {self.user.username}'

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')


    def __str__(self):
        return f'Admin: {self.user.full_name()}'

class Session(models.Model):
    SEASONS = [
        ('Fall', 'Fall'),
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
    ]
    programming_language = models.ForeignKey(
        'ProgrammingLanguage',
        on_delete=models.CASCADE,
        related_name='sessions',
        default=1, 
        help_text="Select the programming language for the session"
    )
    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='sessions')
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ])
    season = models.CharField(
        max_length=20,
        choices=SEASONS,
        default='Fall',
        help_text="Select the season for the session"
    )
    frequency = models.CharField(max_length=20, choices=[('Weekly','Weekly'),('By Weekly','By Weekly')], default='Weekly')
    year = models.PositiveIntegerField(help_text="Enter the year (e.g., 2024)",default=2024)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(default=default_end_time)
    is_availble = models.BooleanField(default=True, help_text="Indicates if the session is available for registration")

    def save(self, *args, **kwargs):
        """Custom save method to validate or enforce conditions."""
        if self.start_time >= self.end_time:
            raise ValueError("Session start time must be earlier than end time.")
        
        if self.end_time < now():
            self.is_availble = False
        
        super(Session, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.programming_language.name} ({self.level}) - {self.season} {self.year} - {self.tutor.user.get_full_name()} - {self.frequency}'


class RequestedStudentSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE,related_name='requested_sessions')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, help_text="Indicates if the session request is approved")

    def approve_request(self):
        if self.is_approved or not self.session.is_availble():
            return
        
        self.session.is_availble = False
        self.session.save()
        StudentSession.objects.create(student=self.student, session=self.session)
        self.is_approved = True
        self.save()

    def save(self, *args, **kwargs):
        """Custom save method to manage session approval logic."""
        if self.is_approved:
            if not self.session.is_availble:
                raise ValueError("Cannot approve a session that is not available.")

            self.session.is_availble = False
            self.session.save()
            StudentSession.objects.get_or_create(student=self.student, session=self.session)

        super(RequestedStudentSession, self).save(*args, **kwargs)

    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f'Request by {self.student.user.get_full_name()} for {self.session} - {status}' 
    
class StudentSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='students')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'session')

    def save(self, *args, **kwargs):
            """Custom save method to validate StudentSession logic."""
            # if not self.session.is_availble:
            #     raise ValueError("Cannot create a session for a student when the session is not available.")

            self.session.is_availble = False
            self.session.save()

            super(StudentSession, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.student.user.get_full_name()} -> {self.session}'
    
    