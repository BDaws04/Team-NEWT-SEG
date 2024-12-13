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

    def test_available_tutors_multiple_pages(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        
        # Create 11 more tutor sessions (12 total)
        for i in range(11):
            tutor = Tutor.objects.create(
                user=User.objects.create(
                    username=f'@tutor{i}',
                    first_name=f'Tutor{i}',
                    last_name='Test',
                    email=f'tutor{i}@example.org'
                )
            )
            
            tutor_session = TutorSession.objects.create(
                tutor=tutor,
                session=self.session
            )
            
            self.requested_session.available_tutor_sessions.add(tutor_session)
            
        # Test first page
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['tutors']), 10)  # First page should have 10 items
        self.assertTrue(response.context['tutors'].has_next())
        self.assertFalse(response.context['tutors'].has_previous())
        
        # Test second page
        response = self.client.get(f"{self.url}?page=2")
        self.assertEqual(len(response.context['tutors']), 2)  # Second page should have 2 items
        self.assertFalse(response.context['tutors'].has_next())
        self.assertTrue(response.context['tutors'].has_previous())
        
        # Test invalid page
        response = self.client.get(f"{self.url}?page=999")
        self.assertEqual(len(response.context['tutors']), 2)  # Should show last page

    def test_available_tutors_post_request(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_tutors.html')
        self.assertIn('tutors', response.context)
        self.assertEqual(response.context['request_id'], self.requested_session.pk)

    def test_get_available_tutors_tutor_redirect(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)
