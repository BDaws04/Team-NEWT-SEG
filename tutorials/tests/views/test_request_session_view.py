from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, RequestedStudentSession, ProgrammingLanguage
from tutorials.forms import SessionForm

class RequestSessionViewTestCase(TestCase):
    """Tests for the request session view."""

    fixtures = ['tutorials/tests/fixtures/default_user.json',
               'tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.student_user = User.objects.get(username='@janedoe')
        self.admin_user = User.objects.get(username='@johndoe')
        self.student = Student.objects.create(user=self.student_user)
        self.url = reverse('request_session')
        self.language = ProgrammingLanguage.objects.create(name='Python')

    def test_request_session_url(self):
        self.assertEqual(self.url, '/request-session/')

    def test_get_request_session_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_request_session_redirects_when_not_student(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_get_request_session_for_student(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_session.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SessionForm))

    def test_successful_session_request(self):
        self.client.login(username=self.student_user.username, password='Password123')
        before_count = RequestedStudentSession.objects.count()
        response = self.client.post(self.url, {
            'programming_language': self.language.id,
            'level': 'beginner',
            'season': 'Fall',
            'year': 2024,
            'frequency': 'Weekly',
            'duration_hours': 1,
        })
        after_count = RequestedStudentSession.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_session.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], 'Session request has been received!')

    def test_unsuccessful_session_request_with_invalid_data(self):
        self.client.login(username=self.student_user.username, password='Password123')
        before_count = RequestedStudentSession.objects.count()
        response = self.client.post(self.url, {})
        after_count = RequestedStudentSession.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_session.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], 'There was an error with your submission.')