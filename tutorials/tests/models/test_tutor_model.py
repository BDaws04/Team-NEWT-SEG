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
        self.language1 = ProgrammingLanguage.objects.create(name='Python')
        self.language2 = ProgrammingLanguage.objects.create(name='JavaScript')

    def test_valid_tutor(self):
        self._assert_tutor_is_valid()

    def test_tutor_str_method(self):
        self.assertEqual(str(self.tutor), f'Tutor: {self.user.get_full_name()}')

    def test_expertise_blank_by_default(self):
        self.assertEqual(self.tutor.expertise.count(), 0)

    def test_expertise_valid_assignment(self):
        self.tutor.expertise.add(self.language1, self.language2)

        self._assert_tutor_is_valid()
        self.assertIn(self.language1, self.tutor.expertise.all())
        self.assertIn(self.language2, self.tutor.expertise.all())

    def test_expertise_list_method(self):
        self.tutor.expertise.add(self.language1, self.language2)

        expertise_list = self.tutor.expertise_list()
        self._assert_tutor_is_valid()
        self.assertEqual(expertise_list, 'Python, JavaScript')

    def _assert_tutor_is_valid(self):
        try:
            self.tutor.full_clean()
        except (ValidationError):
            self.fail('Test tutor should be valid')

    def _assert_tutor_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()