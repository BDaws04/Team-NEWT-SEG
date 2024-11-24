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
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)

    def expertise_list(self):
        return ', '.join([language.name for language in self.expertise.all()])

    expertise_list.short_description = 'Expertise'

    def __str__(self):
        return f'Tutor: {self.user.username}'

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    admin_level = models.CharField(max_length=20, choices=[
        ('junior', 'Junior'),
        ('senior', 'Senior'),
    ])

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
        default=1,  # Replace '1' with the ID of an existing ProgrammingLanguage instance
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
        choices=[('Fall', 'Fall'), ('Spring', 'Spring'), ('Summer', 'Summer')],
        default='Fall',
        help_text="Select the season for the session"
    )
    year = models.PositiveIntegerField(help_text="Enter the year (e.g., 2024)",default=2024)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(default=default_end_time)

    def __str__(self):
        return f'{self.programming_language.name} ({self.level}) - {self.season} {self.year} - {self.tutor.user.get_full_name()}'

class StudentSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='students')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'session')

    def __str__(self):
        return f'{self.student.user.get_full_name()} -> {self.session}'
