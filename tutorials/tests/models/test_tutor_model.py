from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Tutor, ProgrammingLanguage

class TutorModelTestCase(TestCase):
    """Unit tests for the Tutor model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@petrapickles')
        self.tutor = Tutor.objects.create(user=self.user)
        self.language = ProgrammingLanguage.objects.create(name='Python')

    def test_valid_tutor(self):
        self._assert_tutor_is_valid()

    def test_user_must_exist(self):
        self.tutor.user = None
        self._assert_tutor_is_invalid()

    def test_str_method(self):
        expected = f'Tutor: {self.user.full_name()}'
        self.assertEqual(str(self.tutor), expected)

    def test_expertise_blank_by_default(self):
        self.assertEqual(self.tutor.expertise.count(), 0)

    def test_can_add_expertise(self):
        self.tutor.expertise.add(self.language)
        self.assertEqual(self.tutor.expertise.count(), 1)
        self.assertEqual(self.tutor.expertise.first(), self.language)

    def test_can_add_multiple_expertise(self):
        java = ProgrammingLanguage.objects.create(name='Java')
        self.tutor.expertise.add(self.language, java)
        self.assertEqual(self.tutor.expertise.count(), 2)
        self.assertIn(self.language, self.tutor.expertise.all())
        self.assertIn(java, self.tutor.expertise.all())

    def test_expertise_list_method(self):
        self.tutor.expertise.add(self.language)
        self.assertEqual(self.tutor.expertise_list(), 'Python')

    def test_expertise_list_method_multiple_languages(self):
        java = ProgrammingLanguage.objects.create(name='Java')
        self.tutor.expertise.add(self.language, java)
        self.assertEqual(self.tutor.expertise_list(), 'Python, Java')

    def test_expertise_list_method_empty(self):
        self.assertEqual(self.tutor.expertise_list(), '')

    def test_role_set_to_tutor_on_save(self):
        user = User.objects.create(
            username='@newtutor',
            email='newtutor@example.com',
            first_name='New',
            last_name='Tutor'
        )
        tutor = Tutor.objects.create(user=user)
        self.assertEqual(tutor.user.role, User.Roles.TUTOR)

    def test_role_updated_to_tutor_if_different(self):
        user = User.objects.create(
            username='@newtutor2',
            email='newtutor2@example.com',
            first_name='New',
            last_name='Tutor',
            role='STUDENT'
        )
        tutor = Tutor.objects.create(user=user)
        self.assertEqual(tutor.user.role, User.Roles.TUTOR)

    def test_user_must_be_unique(self):
        with self.assertRaises(ValidationError):
            duplicate_tutor = Tutor(user=self.user)
            duplicate_tutor.full_clean()

    def _assert_tutor_is_valid(self):
        try:
            self.tutor.full_clean()
        except ValidationError:
            self.fail('Test tutor should be valid')

    def _assert_tutor_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()