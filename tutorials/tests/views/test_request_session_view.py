from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import User, Student, Tutor, RequestedStudentSession, ProgrammingLanguage
from tutorials.forms import SessionForm

class RequestSessionViewTestCase(TestCase):
    """Tests for the request session view."""

    fixtures = ['tutorials/tests/fixtures/default_user.json',
               'tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')   
        self.student = Student.objects.create(user=self.user)
        self.url = reverse('request_session')

    def test_request_session_url(self):
        """Test request session url is correct."""
        self.assertEqual(self.url, '/request-session/')

    def test_request_session_redirects_when_not_logged_in(self):
        """Test redirect when user is not logged in."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url)

    def test_request_session_redirects_when_logged_in_as_admin(self):
        """Test redirect when user is logged in as admin."""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url)

    def test_get_request_session_for_student(self):
        """Test get request session page."""
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_session.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SessionForm))

    def test_get_request_session_for_tutor(self):
        """Test get request session page for tutor."""
        self.client.login(username='@petrapickles', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_session.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SessionForm))

    def test_post_request_session_for_student_with_valid_data(self):
        """Test post request session page for student with valid data."""
        user = User.objects.get(username='@janedoe')
        student = Student.objects.create(user=user)
        self.client.login(username=user.username, password='Password123')
        programming_language = ProgrammingLanguage.objects.create(name='Python')
        before_count = RequestedStudentSession.objects.count()
        response = self.client.post(self.url, {
            'programming_language': programming_language.id,
            'level': 'beginner',
            'season': 'Fall',
            'year': 2024,
            'frequency': 'Weekly',
            'duration_hours': 1,
        })
        after_count = RequestedStudentSession.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(after_count, before_count + 1)
        self.assertTemplateUsed(response, 'request_session.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], 'Session request has been received!')

    def test_post_request_session_for_student_with_invalid_data(self):
        """Test post request session page for student with invalid data."""
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_session.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], 'There was an error with your submission.')

    def test_post_request_session_for_tutor_with_valid_data(self):
        """Test post request session page for tutor with valid data."""
        user = User.objects.get(username='@petrapickles')
        tutor = Tutor.objects.create(user=user)
        self.client.login(username=user.username, password='Password123')
        programming_language = ProgrammingLanguage.objects.create(name='Python')
        before_count = RequestedStudentSession.objects.count()
        response = self.client.post(self.url, {
            'programming_language': programming_language.id,
            'level': 'beginner',
            'season': 'Fall',
            'year': 2024,
            'frequency': 'Weekly',
            'duration_hours': 1,
        })
        after_count = RequestedStudentSession.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(after_count, before_count + 1)
        self.assertTemplateUsed(response, 'request_session.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], 'Session request has been received!')

    def test_post_request_session_for_tutor_with_invalid_data(self):
        """Test post request session page for tutor with invalid data."""
        self.client.login(username='@petrapickles', password='Password123')
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_session.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], 'There was an error with your submission.')

    