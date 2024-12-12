from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import ProgrammingLanguage

class ProgrammingLanguageModelTestCase(TestCase):
    """Unit tests for the Programming Language model."""

    def setUp(self):
        self.programming_language = ProgrammingLanguage.objects.create(name='Python')

    def test_valid_programming_language(self):
        self._assert_programming_language_is_valid()

    def test_name_cannot_be_blank(self):
        self.programming_language.name = ''
        self._assert_programming_language_is_invalid()

    def test_name_must_be_unique(self):
        duplicate = ProgrammingLanguage(name='Python') 
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_name_must_be_valid_choice(self):
        valid_choices = [choice[0] for choice in ProgrammingLanguage.LANGUAGES]
        for choice in valid_choices:
            self.programming_language.name = choice
            self._assert_programming_language_is_valid()

    def test_name_cannot_be_invalid_choice(self):
        self.programming_language.name = 'InvalidLanguage'
        self._assert_programming_language_is_invalid()

    def test_string_representation(self):
        self.assertEqual(str(self.programming_language), 'Python')

    def test_name_cannot_be_none(self):
        self.programming_language.name = None
        self._assert_programming_language_is_invalid()

    def test_can_create_multiple_valid_languages(self):
        java = ProgrammingLanguage.objects.create(name='Java')
        javascript = ProgrammingLanguage.objects.create(name='JavaScript')
        self.assertEqual(ProgrammingLanguage.objects.count(), 3)
        self.assertIn(java, ProgrammingLanguage.objects.all())
        self.assertIn(javascript, ProgrammingLanguage.objects.all())

    def test_name_case_sensitivity(self):
        # Test that 'Python' and 'python' are treated as different values
        with self.assertRaises(ValidationError):
            lowercase = ProgrammingLanguage(name='python')
            lowercase.full_clean()

    def _assert_programming_language_is_valid(self):
        try:
            self.programming_language.full_clean()
        except ValidationError:
            self.fail('Programming language should be valid')

    def _assert_programming_language_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.programming_language.full_clean()
