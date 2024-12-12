from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import Session, ProgrammingLanguage
from datetime import datetime, timedelta

class SessionModelTestCase(TestCase):
    """Unit tests for the Session model."""

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

    def test_valid_session(self):
        self._assert_session_is_valid()

    def test_programming_language_must_exist(self):
        self.session.programming_language = None
        self._assert_session_is_invalid()

    def test_level_invalid_level(self):
        self.session.level = 'invalid level'
        self._assert_session_is_invalid()

    def test_level_can_be_beginner(self):
        self.session.level = 'beginner'
        self._assert_session_is_valid()
    
    def test_level_can_be_intermediate(self):
        self.session.level = 'intermediate'
        self._assert_session_is_valid()

    def test_level_can_be_advanced(self):
        self.session.level = 'advanced'
        self._assert_session_is_valid()

    def test_level_must_not_be_blank(self):
        self.session.level = ''
        self._assert_session_is_invalid()

    def test_season_invalid_season(self):
        self.session.season = 'invalid season'
        self._assert_session_is_invalid()

    def test_season_can_be_fall(self):
        self.session.season = 'Fall'
        self._assert_session_is_valid()
    
    def test_season_can_be_spring(self):
        self.session.season = 'Spring'
        self._assert_session_is_valid()
    
    def test_season_can_be_summer(self):
        self.session.season = 'Summer'
        self._assert_session_is_valid()

    def test_season_must_not_be_blank(self):
        self.session.season = ''
        self._assert_session_is_invalid()

    def test_default_season_is_fall(self):
        new_session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        self.assertEqual(new_session.season, 'Fall')

    def test_year_can_be_2024(self):
        self.session.year = 2024
        self._assert_session_is_valid()

    def test_year_can_not_be_before_2024(self):
        self.session.year = 2023
        self._assert_session_is_invalid()

    def test_year_can_be_2025(self):
        self.session.year = 2025
        self._assert_session_is_valid()

    def test_year_can_be_2026(self):
        self.session.year = 2026
        self._assert_session_is_valid()

    def test_year_cannot_be_after_2026(self):
        self.session.year = 2027
        self._assert_session_is_invalid()

    def test_year_must_not_be_blank(self):
        self.session.year = None
        self._assert_session_is_invalid()

    def test_frequency_invalid_frequency(self):
        self.session.frequency = 'invalid frequency'
        self._assert_session_is_invalid()

    def test_frequency_can_be_weekly(self):
        self.session.frequency = 'Weekly'
        self._assert_session_is_valid()

    def test_frequency_can_be_bi_weekly(self):
        self.session.frequency = 'Bi-Weekly'
        self._assert_session_is_valid()

    def test_frequency_must_not_be_blank(self):
        self.session.frequency = ''
        self._assert_session_is_invalid()

    def test_default_frequency_is_weekly(self):
        new_session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            duration_hours=2
        )
        self.assertEqual(new_session.frequency, 'Weekly')

    def test_default_duration_hours_is_2(self):
        new_session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
        )
        self.assertEqual(new_session.duration_hours, 2)
    
    def test_duration_hours_can_be_1(self):
        self.session.duration_hours = 1
        self._assert_session_is_valid()

    def test_duration_hours_can_not_be_less_than_1(self):
        self.session.duration_hours = 0
        self._assert_session_is_invalid()

    def test_duration_hours_must_not_be_blank(self):
        self.session.duration_hours = None
        self._assert_session_is_invalid()

    def test_is_available_default_is_true(self):
        self.assertEqual(self.session.is_available, True)

    def test_is_available_can_be_false(self):
        self.session.is_available = False
        self._assert_session_is_valid()

    def test_start_day_and_end_day_are_set_on_creation(self):
        self.assertIsNotNone(self.session.start_day)
        self.assertIsNotNone(self.session.end_day)
        
    def test_str_method(self):
        expected = f"{self.session.programming_language.name} ({self.session.level}) - {self.session.season} {self.session.year} - {self.session.frequency} - {self.session.start_day} to {self.session.end_day}"
        self.assertEqual(str(self.session), expected)

    def _assert_session_is_valid(self):
        try:
            self.session.full_clean()
        except ValidationError:
            self.fail('Test session should be valid')

    def _assert_session_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.session.full_clean()
