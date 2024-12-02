from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Student

class StudentModelTestCase(TestCase):
    """Unit tests for the Student model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@janedoe')
        self.student = Student.objects.create(user=self.user)

    def test_valid_student(self):
        self._assert_student_is_valid()

    def test_student_role_auto_set(self):
        new_user = User.objects.create(
            username='@newuser',
            first_name='new',
            last_name='user',
            email='newuser@gmail.com'
        )
        student = Student.objects.create(user=new_user)

        self._assert_student_is_valid()
        self.assertEqual(student.user.role, User.Roles.STUDENT)

    def test_student_str_method(self):
        self.assertEqual(str(self.student), f'Student: {self.user.get_full_name()}')
    
    def test_student_previous_sessions_blank(self):
        self.assertEqual(self.student.previous_sessions.count(), 0)

    def _assert_student_is_valid(self):
        try:
            self.student.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_student_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student.full_clean()
