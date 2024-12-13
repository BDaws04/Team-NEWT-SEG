from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, StudentSession, Session, TutorSession, Tutor, ProgrammingLanguage

class YourSessionsViewTestCase(TestCase):
    """Tests of the your sessions view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('your_sessions')
        self.student_user = User.objects.get(username='@janedoe')
        self.admin_user = User.objects.get(username='@johndoe')
        self.tutor_user = User.objects.get(username='@petrapickles')
        
        # Create test data
        self.student = Student.objects.create(user=self.student_user)
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
        
        self.student_session = StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session
        )

    def test_your_sessions_url(self):
        self.assertEqual(self.url, '/your-sessions/')

    def test_get_your_sessions_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_your_sessions_with_valid_student(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'your_sessions.html')
        
        # Check context data
        self.assertIn('student_sessions', response.context)
        sessions = response.context['student_sessions']
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], self.student_session)

    def test_get_your_sessions_with_non_student_user(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_your_sessions_shows_only_own_sessions(self):
        # Create another student with session
        other_student_user = User.objects.create_user(
            username='@otherstudent',
            password='Password123',
            role='STUDENT'
        )
        other_student = Student.objects.create(user=other_student_user)
        other_student_session = StudentSession.objects.create(
            student=other_student,
            tutor_session=self.tutor_session
        )

        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        
        sessions = response.context['student_sessions']
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], self.student_session)
        self.assertNotIn(other_student_session, sessions)
