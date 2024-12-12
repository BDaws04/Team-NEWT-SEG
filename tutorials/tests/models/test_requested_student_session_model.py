from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import Session, RequestedStudentSession, User, Student, TutorSession, Tutor, ProgrammingLanguage
from django.utils import timezone

class RequestedStudentSessionModelTestCase(TestCase):
    """Unit tests for the Requested Student Session model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.language = ProgrammingLanguage.objects.create(name='Python')
        self.session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        self.student_user = User.objects.get(username='@janedoe')
        self.student = Student.objects.create(user=self.student_user)
        self.requested_session = RequestedStudentSession.objects.create(
            student=self.student,
            session=self.session
        )

    def test_valid_requested_session(self):
        self._assert_requested_session_is_valid()

    def test_student_must_exist(self):
        self.requested_session.student = None
        self._assert_requested_session_is_invalid()

    def test_session_must_exist(self):
        self.requested_session.session = None
        self._assert_requested_session_is_invalid()

    def test_is_approved_default_is_false(self):
        self.assertFalse(self.requested_session.is_approved)

    def test_cannot_modify_approved_request(self):
        self.requested_session.is_approved = True
        
        with self.assertRaises(ValueError):
            self.requested_session.session = Session.objects.create(
                programming_language=self.language,
                level='intermediate',
                season='Spring',
                year=2024,
                frequency='Weekly',
                duration_hours=2
            )
            self.requested_session.save()

    def test_available_tutor_sessions_populated(self):
        tutor_user = User.objects.create(
            username='@newuser',
            password='Password123',
            email='newuser@example.com'
        )
        tutor = Tutor.objects.create(user=tutor_user)
        tutor_session = TutorSession.objects.create(
            tutor=tutor,
            session=self.session
        )

        new_request = RequestedStudentSession.objects.get(
            student=self.student,
            session=self.session
        )
        new_request.save()
        self.assertIn(tutor_session, new_request.available_tutor_sessions.all())

    def test_str_method(self):
        expected = f"Request by {self.student.user.full_name()} for {self.session} - Pending"
        self.assertEqual(str(self.requested_session), expected)

    def test_str_method_when_approved(self):
        self.requested_session.is_approved = True
        expected = f"Request by {self.student.user.full_name()} for {self.session} - Approved"
        self.assertEqual(str(self.requested_session), expected)

    def test_request_date_set_on_creation(self):
        self.assertIsNotNone(self.requested_session.requested_at)
        self.assertLessEqual(self.requested_session.requested_at.date(), timezone.now().date())

    def test_student_session_unique_together(self):
        with self.assertRaises(ValidationError):
            duplicate_request = RequestedStudentSession(
                student=self.student,
                session=self.session
            )
            duplicate_request.full_clean()

    def test_can_create_multiple_requests_for_different_sessions(self):
        new_session = Session.objects.create(
            programming_language=self.language,
            level='intermediate',
            season='Spring',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        new_request = RequestedStudentSession.objects.create(
            student=self.student,
            session=new_session
        )
        self._assert_requested_session_is_valid()
        self.assertNotEqual(new_request.session, self.requested_session.session)

    def _assert_requested_session_is_valid(self):
        try:
            self.requested_session.full_clean()
        except ValidationError:
            self.fail('Test requested session should be valid')

    def _assert_requested_session_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.requested_session.full_clean()
