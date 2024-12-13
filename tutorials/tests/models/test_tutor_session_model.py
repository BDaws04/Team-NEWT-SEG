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
        self._assert_tutor_session_is_valid()

    def test_tutor_must_exist(self):
        self.tutor_session.tutor = None
        self._assert_tutor_session_is_invalid()

    def test_session_must_exist(self):
        self.tutor_session.session = None
        self._assert_tutor_session_is_invalid()

    def test_tutor_session_can_be_created(self):
        new_user = User.objects.create(
            username='@newuser',
            password='Password123',
            email='newuser@example.com'
        )
        new_tutor = Tutor.objects.create(user=new_user)
        new_session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        tutor_session = TutorSession.objects.create(
            tutor=new_tutor,
            session=new_session
        )
        self.assertIsNotNone(tutor_session.id)

    def test_tutor_session_can_be_deleted(self):
        tutor_session_id = self.tutor_session.id
        self.tutor_session.delete()
        with self.assertRaises(TutorSession.DoesNotExist):
            TutorSession.objects.get(id=tutor_session_id)

    def test_str_method(self):
        expected = f"Tutor: {self.tutor.user.full_name()} - Session: {self.session}"
        self.assertEqual(str(self.tutor_session), expected)

    def test_tutor_session_unique_together(self):
        with self.assertRaises(ValidationError):
            duplicate_tutor_session = TutorSession(
                tutor=self.tutor,
                session=self.session
            )
            duplicate_tutor_session.full_clean()

    def test_tutor_session_can_be_updated(self):
        new_session = Session.objects.create(
            programming_language=self.language,
            level='advanced',
            season='Spring',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        self.tutor_session.session = new_session
        self.tutor_session.save()
        self._assert_tutor_session_is_valid()
        updated_session = TutorSession.objects.get(id=self.tutor_session.id)
        self.assertEqual(updated_session.session, new_session)

    def test_tutor_expertise_matches_session_language(self):
        self.tutor.expertise.add(self.language)
        self._assert_tutor_session_is_valid()

    def test_tutor_session_creation_date(self):
        self.assertIsNotNone(self.tutor_session.created_at)
        self.assertLessEqual(self.tutor_session.created_at.date(), timezone.now().date())

    def _assert_tutor_session_is_valid(self):
        try:
            self.tutor_session.full_clean()
        except ValidationError:
            self.fail('Test tutor session should be valid')

    def _assert_tutor_session_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tutor_session.full_clean()
