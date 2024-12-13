from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Tutor, Session, TutorSession, StudentSession, ProgrammingLanguage

class SessionDetailsViewTestCase(TestCase):
    """Tests of the session details view."""

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

        self.url = reverse('session_details', kwargs={'session_id': self.student_session.id})

    def test_session_details_url(self):
        self.assertEqual(self.url, f'/session/{self.student_session.id}/')

    def test_get_session_details_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_session_details_with_valid_id(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'session_details.html')
        
        # Check context data
        self.assertIn('tutor_session', response.context)
        tutor_session = response.context['tutor_session']
        self.assertEqual(tutor_session, self.tutor_session)

    def test_get_session_details_with_invalid_id(self):
        self.client.login(username=self.student_user.username, password='Password123')
        url = reverse('session_details', kwargs={'session_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_session_details_for_other_student_session(self):
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
        url = reverse('session_details', kwargs={'session_id': other_student_session.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_session_details_post_request(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'session_details.html')
        self.assertIn('tutor_session', response.context)

    def test_get_session_details_tutor_access(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'session_details.html')
        self.assertIn('tutor_session', response.context)
        tutor_session = response.context['tutor_session']
        self.assertEqual(tutor_session, self.tutor_session)
