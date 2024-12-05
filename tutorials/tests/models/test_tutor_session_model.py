from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import Session, TutorSession, User, Tutor, ProgrammingLanguage
from django.utils import timezone

class TutorSessionModelTestCase(TestCase):
    """Unit tests for the Tutor Session model."""

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
        self.user = User.objects.get(username='@petrapickles')
        self.tutor = Tutor.objects.create(user=self.user)
        self.tutor_session = TutorSession.objects.create(tutor=self.tutor, session=self.session)

    def test_valid_tutor_session(self):
        self._assert_session_is_valid()

    def test_created_at_is_calculated_correctly(self):
        now = timezone.now()
        self.assertAlmostEqual(now, self.tutor_session.created_at)

    def test_notes_is_blank_by_default(self):
        self.assertEqual(self.tutor_session.notes, None)

    def test_str_method(self):
        self.assertEqual(str(self.tutor_session), f'Tutor: {self.tutor.user.get_full_name()} - Session: {self.session}')
