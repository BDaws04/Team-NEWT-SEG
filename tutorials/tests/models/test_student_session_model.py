from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import Session, StudentSession, User, Student, TutorSession, Tutor, ProgrammingLanguage
from django.utils import timezone

class StudentSessionModelTestCase(TestCase):
    """Unit tests for the Student Session model."""

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
        self.tutor_user = User.objects.get(username='@petrapickles')
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            session=self.session
        )
        self.student_session = StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session
        )

    def test_valid_student_session(self):
        self._assert_student_session_is_valid()

    def test_student_must_exist(self):
        self.student_session.student = None
        self._assert_student_session_is_invalid()

    def test_tutor_session_must_exist(self):
        self.student_session.tutor_session = None
        self._assert_student_session_is_invalid()

    def test_default_status_is_send_invoice(self):
        self.assertEqual(self.student_session.status, 'Send Invoice')

    def test_session_marked_unavailable_on_save(self):
        self.assertFalse(self.student_session.tutor_session.session.is_available)

    def test_str_method(self):
        expected = f'{self.student.user.full_name()} -> {self.tutor_session}'
        self.assertEqual(str(self.student_session), expected)

    def test_unique_together_constraint(self):
        with self.assertRaises(ValidationError):
            duplicate_session = StudentSession(
                student=self.student,
                tutor_session=self.tutor_session
            )
            duplicate_session.full_clean()

    def test_student_session_can_be_created(self):
        new_student_user = User.objects.create(
            username='@newstudent',
            email='newstudent@example.com',
            first_name='New',
            last_name='Student'
        )
        new_student = Student.objects.create(user=new_student_user)
        new_student_session = StudentSession.objects.create(
            student=new_student,
            tutor_session=self.tutor_session
        )
        self.assertIsNotNone(new_student_session.id)

    def test_student_session_can_be_deleted(self):
        student_session_id = self.student_session.id
        self.student_session.delete()
        with self.assertRaises(StudentSession.DoesNotExist):
            StudentSession.objects.get(id=student_session_id)

    def test_student_session_creation_date(self):
        self.assertIsNotNone(self.student_session.registered_at)
        self.assertLessEqual(self.student_session.registered_at.date(), timezone.now().date())
        
    def test_invalid_status(self):
        self.student_session.status = 'Invalid Status'
        self._assert_student_session_is_invalid()

    def test_status_cannot_be_blank(self):
        self.student_session.status = ''
        self._assert_student_session_is_invalid()

    def test_student_session_can_be_updated(self):
        new_session = Session.objects.create(
            programming_language=self.language,
            level='advanced',
            season='Spring',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        new_tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            session=new_session
        )
        self.student_session.tutor_session = new_tutor_session
        self.student_session.save()
        self._assert_student_session_is_valid()
        updated_session = StudentSession.objects.get(id=self.student_session.id)
        self.assertEqual(updated_session.tutor_session, new_tutor_session)

    def _assert_student_session_is_valid(self):
        try:
            self.student_session.full_clean()
        except ValidationError:
            self.fail('Test student session should be valid')

    def _assert_student_session_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student_session.full_clean()
