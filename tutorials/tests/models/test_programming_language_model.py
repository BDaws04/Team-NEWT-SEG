from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import ProgrammingLanguage

class ProgrammingLanguageModelTestCase(TestCase):
    """Unit tests for the Programming Language model."""

    def setUp(self):
        self.programming_language = ProgrammingLanguage.objects.create(name='Python')

    def test_valid_programming_language(self):
        self._assert_programming_language_is_valid()

    def test_programming_language_may_be_blank(self):
        self.programming_language.name = ''
        self._assert_programming_language_is_invalid()

    def test_programming_language_must_be_unique(self):
        duplicate_language = ProgrammingLanguage(name='Python')
        with self.assertRaises(ValidationError):
            duplicate_language.full_clean()

    def test_programming_language_must_be_valid_choice(self):
        valid_languages = ['Python', 'Java', 'C++', 'JavaScript', 'Ruby', 'PHP', 'Go', 'Swift', 'Kotlin', 'Rust']
        for lang in valid_languages:
            self.programming_language.name = lang
            self._assert_programming_language_is_valid()

    def test_programing_language_invalid_choice(self):
        invalid_language = 'InvalidLanguage'
        self.programming_language.name = invalid_language
        self._assert_programming_language_is_invalid()

    def test_programming_language_str_method(self):
        self.assertEqual(str(self.programming_language), 'Python')

    def _assert_programming_language_is_valid(self):
        try:
            self.programming_language.full_clean()
        except (ValidationError):
            self.fail('Test language should be valid')

    def _assert_programming_language_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.programming_language.full_clean()
