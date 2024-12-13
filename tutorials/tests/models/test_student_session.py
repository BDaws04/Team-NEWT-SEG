from django.test import TestCase
from tutorials.models import StudentSession, Student, Tutor, TutorSession, Session, ProgrammingLanguage, User
from datetime import datetime

class StudentSessionTestCase(TestCase):
    def setUp(self):
        # Create a programming language
        self.language = ProgrammingLanguage.objects.create(name='Python')

        # Create a student user and profile
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpass',
            role='STUDENT'
        )
        self.student = Student.objects.create(user=self.student_user)

        # Create a tutor user and profile
        self.tutor_user = User.objects.create_user(
            username='tutor1',
            email='tutor1@example.com',
            password='testpass',
            role='TUTOR'
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create a session
        self.session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=2,
            start_day=datetime(2024, 9, 16),
            end_day=datetime(2024, 12, 16),
            is_available=True
        )

        # Create a tutor session
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            session=self.session
        )

    def test_create_student_session(self):
        """Test creating a valid StudentSession."""
        student_session = StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session,
            status='Send Invoice'
        )
        self.assertEqual(student_session.student, self.student)
        self.assertEqual(student_session.tutor_session, self.tutor_session)
        self.assertEqual(student_session.status, 'Send Invoice')
        self.assertFalse(self.tutor_session.session.is_available)  # Ensure the session is no longer available

    def test_unique_together_constraint(self):
        """Test the unique_together constraint for StudentSession."""
        # Create the first StudentSession
        StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session,
            status='Send Invoice'
        )

        # Attempt to create a duplicate StudentSession
        with self.assertRaises(Exception) as context:
            StudentSession.objects.create(
                student=self.student,
                tutor_session=self.tutor_session,
                status='Payment Pending'
            )
        self.assertTrue('UNIQUE constraint' in str(context.exception))

    def test_str_representation(self):
    # Create a StudentSession instance
        student_session = StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session,
            status='Approved'
        )

        # Expected string representation
        expected_str = f'{self.student_user.full_name()} -> {self.tutor_session}'

        # Normalize both actual and expected strings
        actual_str = str(student_session).strip()
        expected_str = expected_str.strip()

        # Assertion
        self.assertEqual(actual_str, expected_str, 
                        f"String mismatch:\nExpected: '{expected_str}'\nActual: '{actual_str}'")


    def test_save_method(self):
        """Test the save method of StudentSession."""
        # Verify the session is available before creating a StudentSession
        self.assertTrue(self.session.is_available)

        # Create a StudentSession
        student_session = StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session,
            status='Approved'
        )

        # Verify that the session is no longer available
        self.session.refresh_from_db()
        self.assertFalse(self.session.is_available)

    def test_student_session_defaults(self):
        """Test default values in StudentSession."""
        student_session = StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session
        )
        self.assertEqual(student_session.status, 'Send Invoice')
