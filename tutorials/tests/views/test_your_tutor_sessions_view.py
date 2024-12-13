from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, StudentSession, Session, TutorSession, Tutor, ProgrammingLanguage

class YourTutorSessionsViewTestCase(TestCase):
    """Tests of the your tutor sessions view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('your_tutor_sessions')
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')
        
        # Create test data
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        
        self.language = ProgrammingLanguage.objects.create(name='Python')
        self.session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            session=self.session
        )

    def test_your_tutor_sessions_url(self):
        self.assertEqual(self.url, '/your-tutor-sessions/')

    def test_get_your_tutor_sessions_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_your_tutor_sessions_with_valid_tutor(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'your_tutor_sessions.html')
        
        # Check context data
        self.assertIn('tutor_sessions', response.context)
        sessions = response.context['tutor_sessions']
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], self.tutor_session)

    def test_get_your_tutor_sessions_with_non_tutor_user(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_your_tutor_sessions_shows_only_own_sessions(self):
        # Create another tutor with session
        other_tutor_user = User.objects.create_user(
            username='@othertutor',
            password='Password123',
            role='TUTOR'
        )
        other_tutor = Tutor.objects.create(user=other_tutor_user)
        other_tutor_session = TutorSession.objects.create(
            tutor=other_tutor,
            session=self.session
        )

        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        
        sessions = response.context['tutor_sessions']
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], self.tutor_session)
        self.assertNotIn(other_tutor_session, sessions)

    def test_get_your_tutor_sessions_student_redirect(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_your_tutor_sessions_post_request(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'your_tutor_sessions.html')
        self.assertIn('tutor_sessions', response.context)

    def test_get_your_tutor_sessions_with_tutor_role_no_profile(self):
        # Create a user with tutor role but no Tutor profile
        user_without_profile = User.objects.create_user(
            username='@notutor',
            password='Password123',
            role='TUTOR'
        )
        self.client.login(username=user_without_profile.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
