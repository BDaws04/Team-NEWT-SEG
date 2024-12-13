from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Tutor, Session, TutorSession, RequestedStudentSession, ProgrammingLanguage

class AvailableTutorsViewTestCase(TestCase):
    """Tests of the available tutors view."""

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

        self.requested_session = RequestedStudentSession.objects.create(
            student=self.student,
            session=self.session
        )
        
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            session=self.session
        )
        
        self.requested_session.available_tutor_sessions.add(self.tutor_session)

        self.url = reverse('available_tutors', kwargs={'request_id': self.requested_session.pk})

    def test_available_tutors_url(self):
        self.assertEqual(self.url, f'/available-tutors/{self.requested_session.pk}/')

    def test_get_available_tutors_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_available_tutors_redirects_when_not_admin(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_get_available_tutors_for_admin(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_tutors.html')
        
        # Check context data
        self.assertIn('tutors', response.context)
        self.assertIn('request_id', response.context)
        tutors = response.context['tutors']
        self.assertEqual(len(tutors), 1)
        self.assertEqual(tutors[0], self.tutor_session)
        self.assertEqual(response.context['request_id'], self.requested_session.pk)

    def test_available_tutors_pagination(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_tutors.html')
        tutors = response.context['tutors']
        self.assertEqual(len(tutors), 1)
        self.assertEqual(tutors.number, 1)
        self.assertEqual(tutors.paginator.num_pages, 1)

    def test_available_tutors_non_existing_request(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        non_existing_url = reverse('available_tutors', kwargs={'request_id': 9999})
        response = self.client.get(non_existing_url)
        self.assertEqual(response.status_code, 404)
