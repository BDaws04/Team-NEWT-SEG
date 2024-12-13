from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, StudentSession, Session, TutorSession, Tutor, ProgrammingLanguage

class RemoveSessionViewTestCase(TestCase):
    """Tests of the remove session view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
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

        self.url = reverse('remove_session', kwargs={'session_id': self.student_session.pk})

    def test_remove_session_url(self):
        self.assertEqual(self.url, f'/student-sessions/remove-session/{self.student_session.pk}/')

    def test_remove_session_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_remove_session_redirects_when_not_admin(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_remove_session_for_admin(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('student_sessions'), status_code=302, target_status_code=200)
        
        # Check that session was deleted
        with self.assertRaises(StudentSession.DoesNotExist):
            StudentSession.objects.get(pk=self.student_session.pk)

    def test_remove_session_non_existing_session(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        non_existing_url = reverse('remove_session', kwargs={'session_id': 9999})
        response = self.client.get(non_existing_url)
        self.assertEqual(response.status_code, 404)
