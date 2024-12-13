from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Session, RequestedStudentSession, ProgrammingLanguage

class RequestedSessionsViewTestCase(TestCase):
    """Tests of the requested sessions view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('requested_sessions')
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        
        # Create test data
        self.student = Student.objects.create(user=self.student_user)
        
        self.language = ProgrammingLanguage.objects.create(name='Python')
        self.session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        
        self.requested_session = RequestedStudentSession.objects.create(
            student=self.student,
            session=self.session,
            is_approved=False
        )

    def test_requested_sessions_url(self):
        self.assertEqual(self.url, '/requested-sessions/')

    def test_get_requested_sessions_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_requested_sessions_for_student(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requested_sessions.html')
        
        # Check context data
        self.assertIn('requested_sessions', response.context)
        sessions = response.context['requested_sessions']
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], self.requested_session)

    def test_requested_sessions_shows_only_own_requests(self):
        # Create another student with requested session
        other_student_user = User.objects.create_user(
            username='@otherstudent',
            password='Password123',
            role='STUDENT'
        )
        other_student = Student.objects.create(user=other_student_user)
        other_requested_session = RequestedStudentSession.objects.create(
            student=other_student,
            session=self.session,
            is_approved=False
        )

        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        
        sessions = response.context['requested_sessions']
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], self.requested_session)
        self.assertNotIn(other_requested_session, sessions)

    def test_non_student_gets_empty_list(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requested_sessions.html')
        sessions = response.context['requested_sessions']
        self.assertEqual(len(sessions), 0)
