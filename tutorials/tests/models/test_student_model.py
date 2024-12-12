from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Student, Session, ProgrammingLanguage
from django.utils import timezone

class StudentModelTestCase(TestCase):
    """Unit tests for the Student model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@janedoe')
        self.student = Student.objects.create(user=self.user)
        self.language = ProgrammingLanguage.objects.create(name='Python')

    def test_valid_student(self):
        self._assert_student_is_valid()

    def test_user_must_exist(self):
        self.student.user = None
        self._assert_student_is_invalid()

    def test_enrollment_date_set_on_creation(self):
        self.assertIsNotNone(self.student.enrollment_date)
        self.assertLessEqual(self.student.enrollment_date, timezone.now().date())

    def test_str_method(self):
        expected = f'Student: {self.user.full_name()}'
        self.assertEqual(str(self.student), expected)
    
    def test_previous_sessions_blank_by_default(self):
        self.assertEqual(self.student.previous_sessions.count(), 0)

    def test_can_add_previous_sessions(self):
        session = Session.objects.create(
            programming_language=self.language,
            level='Beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=1
        )
        self.student.previous_sessions.add(session)
        self.assertEqual(self.student.previous_sessions.count(), 1)
        self.assertEqual(self.student.previous_sessions.first(), session)

    def test_can_add_multiple_previous_sessions(self):
        session1 = Session.objects.create(
            programming_language=self.language,
            level='Beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=1
        )
        session2 = Session.objects.create(
            programming_language=self.language,
            level='Intermediate',
            season='Spring',
            year=2024,
            frequency='Weekly',
            duration_hours=1
        )
        self.student.previous_sessions.add(session1, session2)
        self.assertEqual(self.student.previous_sessions.count(), 2)
        self.assertIn(session1, self.student.previous_sessions.all())
        self.assertIn(session2, self.student.previous_sessions.all())

    def test_role_set_to_student_on_save(self):
        user = User.objects.create(
            username='@newstudent',
            email='newstudent@example.com',
            first_name='New',
            last_name='Student'
        )
        student = Student.objects.create(user=user)
        self.assertEqual(student.user.role, User.Roles.STUDENT)

    def test_role_updated_to_student_if_different(self):
        user = User.objects.create(
            username='@newstudent2',
            email='newstudent2@example.com',
            first_name='New',
            last_name='Student',
            role='TUTOR'
        )
        student = Student.objects.create(user=user)
        self.assertEqual(student.user.role, User.Roles.STUDENT)

    def test_user_must_be_unique(self):
        with self.assertRaises(ValidationError):
            duplicate_student = Student(user=self.user)
            duplicate_student.full_clean()

    def _assert_student_is_valid(self):
        try:
            self.student.full_clean()
        except ValidationError:
            self.fail('Test student should be valid')

    def _assert_student_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student.full_clean()
