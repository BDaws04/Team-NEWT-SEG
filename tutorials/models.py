from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.core.validators import MinValueValidator
from datetime import date, datetime, timedelta
from datetime import datetime, timedelta
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

def calculate_end_date(start_date, duration_weeks):
    return start_date + timedelta(weeks=duration_weeks,days=4)

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

    def save(self, *args, **kwargs):
        # Automatically set the role to 'STUDENT' when a student object is created
        if not self.user.role:
            self.user.role = User.Roles.STUDENT
            self.user.save()
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return f'Student: {self.user.full_name()}'


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

    def save(self, *args, **kwargs):
        # Automatically set the role to 'TUTOR' when a tutor object is created
        if not self.user.role:
            self.user.role = User.Roles.TUTOR
            self.user.save()
        super(Tutor, self).save(*args, **kwargs)

    def expertise_list(self):
        return ', '.join([language.name for language in self.expertise.all()])

    expertise_list.short_description = 'Expertise'

    def __str__(self):
        return f'Tutor: {self.user.full_name()}'

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    def __str__(self):
        return f'Admin: {self.user.full_name()}'


def calculate_end_date(start_date, duration_weeks):
    return start_date + timedelta(weeks=duration_weeks,days=4)


class Session(models.Model):
    SEASONS = [
        ('Fall', 'Fall'),
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
    ]

    TERM_START_DATES = {
        2024: {
            'Fall': datetime(2024, 9, 16),
            'Spring': datetime(2024, 1, 8),
            'Summer': datetime(2024, 5, 6),  # Starts in May
        },
        2025: {
            'Fall': datetime(2025, 9, 15),
            'Spring': datetime(2025, 1, 6),
            'Summer': datetime(2025, 5, 5),  # Starts in May
        },
        2026: {
            'Fall': datetime(2026, 9, 14),
            'Spring': datetime(2026, 1, 5),
            'Summer': datetime(2026, 5, 4),  # Starts in May
        },
    }

    programming_language = models.ForeignKey(
        'ProgrammingLanguage',
        on_delete=models.CASCADE,
        related_name='sessions',
        default=1,
        help_text="Select the programming language for the session"
    )
    level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ]
    )
    season = models.CharField(
        max_length=20,
        choices=SEASONS,
        default='Fall',
        help_text="Select the season for the session"
    )
    year = models.PositiveIntegerField(
        help_text="Enter the year (e.g., 2024)",
        validators=[MinValueValidator(2024)]
    )
    frequency = models.CharField(
        max_length=20,
        choices=[('Weekly', 'Weekly'), ('Bi-Weekly', 'Bi-Weekly')],
        default='Weekly'
    )
    duration_hours = models.PositiveIntegerField(
        default=2,
        help_text="Duration of each session in hours (1-2 hours).",
        validators=[MinValueValidator(1)]
    )
    start_day = models.DateField(help_text="Start date of the session term.")
    end_day = models.DateField(help_text="End date of the session term.")
    is_available = models.BooleanField(
        default=True,
        help_text="Indicates if the session is available for registration"
    )

    def save(self, *args, **kwargs):
        if self.year not in self.TERM_START_DATES:
            raise ValueError(f"Start dates not configured for year {self.year}.")
        if self.season not in self.TERM_START_DATES[self.year]:
            raise ValueError(f"Start date for {self.season} in {self.year} not configured.")

        self.start_day = self.TERM_START_DATES[self.year][self.season]
        duration_weeks = 12 if self.season == 'Fall' else (11 if self.season == 'Spring' else 6)  # Adjust summer duration

        self.end_day = calculate_end_date(self.start_day, duration_weeks)

        
        if isinstance(self.end_day, datetime):
            self.end_day = self.end_day.date()

        super(Session, self).save(*args, **kwargs)

    def __str__(self):
        return (f'{self.programming_language.name} ({self.level}) - {self.season} {self.year} - '
                f'{self.frequency} - {self.start_day} to {self.end_day}')


class TutorSession(models.Model):
    tutor = models.ForeignKey(
        'Tutor',
        on_delete=models.CASCADE,
        related_name='tutor_sessions'
    )
    session = models.ForeignKey(
        'Session',
        on_delete=models.CASCADE,
        related_name='tutor_sessions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Tutor: {self.tutor.user.get_full_name()} - Session: {self.session}'

    def assign_to_tutor(self, tutor, session):
        self.tutor = tutor
        self.session = session
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        student_sessions = RequestedStudentSession.objects.filter(
            is_approved=False,
            session__programming_language=self.session.programming_language,
            session__level=self.session.level,
            session__season=self.session.season,
            session__year=self.session.year
        )

        for student_session in student_sessions:
            student_session.available_tutor_sessions.add(self)
            student_session.save()
    
            if student_session.session.programming_language == self.session.programming_language and \
               student_session.session.level == self.session.level and \
               student_session.session.season == self.session.season and \
               student_session.session.year == self.session.year:
                
                student_session.available_tutor_sessions.add(self)
                student_session.save()
        super(TutorSession, self).save(*args, **kwargs)


# class RequestedStudentSession(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='requested_sessions')
#     session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='requests')
#     requested_at = models.DateTimeField(auto_now_add=True)
#     is_approved = models.BooleanField(default=False, help_text="Indicates if the session request is approved")
#     available_tutor_sessions = models.ManyToManyField('TutorSession', related_name='requested_sessions', blank=True)

#     def approve_request(self, tutor_session):
#         if self.is_approved or not tutor_session.session.is_available:
#             raise ValueError("Cannot approve a request for a session that is not available or already approved.")
    
#         tutor_session.session.is_available = False
#         tutor_session.session.save()

    
#         student_session = StudentSession.objects.create(student=self.student, tutor_session=tutor_session)

   
#         self.is_approved = True
#         self.save()

#         return student_session

#     def filter_unapproved_requests(self):
#         return RequestedStudentSession.objects.filter(is_approved=False)

#     def save(self, *args, **kwargs):
#         if self.is_approved:
#             raise ValueError("Cannot modify an already approved request.")
        
#         super(RequestedStudentSession, self).save(*args, **kwargs)

#         tutor_sessions = TutorSession.objects.all()
#         for tutor_session in tutor_sessions:
#             if tutor_session.session.programming_language == self.session.programming_language and tutor_session.session.level == self.session.level and tutor_session.session.season == self.session.season and tutor_session.session.year == self.session.year:
#                 self.available_tutor_sessions.add(tutor_session)

#         super(RequestedStudentSession, self).save(*args, **kwargs)

#     def __str__(self):
#         status = "Approved" if self.is_approved else "Pending"
#         return f'Request by {self.student.user.get_full_name()} for {self.session} - {status}'

class RequestedStudentSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='requested_sessions')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, help_text="Indicates if the session request is approved")
    available_tutor_sessions = models.ManyToManyField('TutorSession', related_name='requested_sessions', blank=True)

    class Meta:
        unique_together = ('student', 'session')
        ordering = ['-requested_at']
        verbose_name = "Requested Student Session"
        verbose_name_plural = "Requested Student Sessions"

    def approve_request(self, tutor_session):
        if self.is_approved or not tutor_session.session.is_available:
            raise ValueError("Cannot approve a request for a session that is not available or already approved.")
        tutor_session.session.is_available = False
        tutor_session.session.save()
        student_session = StudentSession.objects.create(student=self.student, tutor_session=tutor_session)
        self.is_approved = True
        self.save()
        return student_session

    def save(self, *args, **kwargs):
        # Ensure we're not modifying an already approved request
        if self.is_approved and 'is_approved' not in kwargs.get('update_fields', []):
            raise ValueError("Cannot modify an already approved request.")
        
        # Perform the standard save operation
        super(RequestedStudentSession, self).save(*args, **kwargs)

        # Automatically populate available tutor sessions for a new request
        if not self.is_approved:
            eligible_tutor_sessions = TutorSession.objects.filter(
                session__programming_language=self.session.programming_language,
                session__level=self.session.level,
                session__season=self.session.season,
                session__year=self.session.year,
            )
            self.available_tutor_sessions.set(eligible_tutor_sessions)


    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f'Request by {self.student.user.full_name()} for {self.session} - {status}'


class StudentSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    tutor_session = models.ForeignKey(TutorSession, on_delete=models.CASCADE, related_name='student_sessions')
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Send Invoice', 'Send Invoice'), ('Payment Pending', 'Payment Pending'), ('Approved', 'Approved'), ('Cancelled', 'Cancelled')], default='Send Invoice')

    class Meta:
        unique_together = ('student', 'tutor_session')
        verbose_name = "Student Session"
        verbose_name_plural = "Student Sessions"

    def save(self, *args, **kwargs):
        if not self.tutor_session.session.is_available:
            raise ValueError("Cannot create a session for a student when the session is not available.")
            raise ValueError("Cannot register a student for a session that is unavailable.")
        self.tutor_session.session.is_available = False
        self.tutor_session.session.save()
        super(StudentSession, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.student.user.full_name()} -> {self.tutor_session}'

# class StudentSession(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
#     tutor_session = models.ForeignKey(TutorSession, on_delete=models.CASCADE, related_name='student_sessions')
#     registered_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('student', 'tutor_session')

#     def save(self, *args, **kwargs):
#         if not self.tutor_session.session.is_available:
#             raise ValueError("Cannot create a session for a student when the session is not available.")
#         self.tutor_session.session.is_available = False
#         self.tutor_session.session.save()
#         super(StudentSession, self).save(*args, **kwargs)

#     def __str__(self):
#         return f'{self.student.user.get_full_name()} -> {self.tutor_session}'

class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]

    session = models.ForeignKey(
        'StudentSession',
        on_delete=models.CASCADE,
        related_name='invoices',
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.session:
            session = self.session.tutor_session.session
            
            if session.duration_hours <= 1:
                self.amount = Decimal('30.00')
            elif session.duration_hours <= 2:
                self.amount = Decimal('50.00')
                
            # Set default due date if not provided
            if not self.due_date:
                self.due_date = timezone.now().date() + timedelta(days=30)  # Due in 30 days
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.id} - {self.session.student.user.get_full_name()} - {self.payment_status}"

    def mark_as_paid(self):
        from django.utils import timezone
        self.payment_status = 'PAID'
        self.payment_date = timezone.now().date()
        self.save()

    """
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
    frequency = models.CharField(max_length=20, choices=[('Weekly','Weekly'),('Bi-Weekly','Bi-Weekly')], default='Weekly')
    year = models.PositiveIntegerField(help_text="Enter the year (e.g., 2024)",default=2024)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(default=default_end_time)
    is_availble = models.BooleanField(default=True, help_text="Indicates if the session is available for registration")

    def save(self, *args, **kwargs):
        if self.start_time >= self.end_time:
            raise ValueError("Session start time must be earlier than end time.")
        
        if self.end_time < now():
            self.is_availble = False
        
        super(Session, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.programming_language.name} ({self.level}) - {self.season} {self.year} - {self.tutor.user.get_full_name()} - {self.frequency}'
    """
