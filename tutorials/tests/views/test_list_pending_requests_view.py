"""Tests of the list pending requests view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Session, RequestedStudentSession, ProgrammingLanguage

class ListPendingRequestsViewTestCase(TestCase):
    """Tests of the list pending requests view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('pending_requests')
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        
        self.student = Student.objects.create(user=self.student_user)
        
        # Create test data
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

    def test_list_pending_requests_url(self):
        self.assertEqual(self.url, '/pending-requests/')

    def test_get_list_pending_requests_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_list_pending_requests_redirects_when_not_admin(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_get_list_pending_requests_for_admin(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pending_requests.html')
        
        # Check context data
        self.assertIn('requests', response.context)
        self.assertIn('levels', response.context)
        self.assertIn('years', response.context)
        self.assertIn('languages', response.context)
        
        # Verify the pending request is in the context
        self.assertEqual(list(response.context['requests']), [self.requested_session])

    def test_list_pending_requests_with_filters(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        
        # Test with level filter
        response = self.client.get(f"{self.url}?level=beginner")
        self.assertEqual(len(response.context['requests']), 1)
        
        response = self.client.get(f"{self.url}?level=advanced")
        self.assertEqual(len(response.context['requests']), 0)
        
        # Test with year filter
        response = self.client.get(f"{self.url}?year=2024")
        self.assertEqual(len(response.context['requests']), 1)
        
        response = self.client.get(f"{self.url}?year=2023")
        self.assertEqual(len(response.context['requests']), 0)
        
        # Test with language filter
        response = self.client.get(f"{self.url}?language=Python")
        self.assertEqual(len(response.context['requests']), 1)
        
        response = self.client.get(f"{self.url}?language=Java")
        self.assertEqual(len(response.context['requests']), 0)

    def test_list_pending_requests_pagination(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        
        # Create 11 more requests (12 total)
        for i in range(11):
            session = Session.objects.create(
                programming_language=self.language,
                level='beginner',
                season='Fall',
                year=2024,
                frequency='Weekly',
                duration_hours=2
            )
            RequestedStudentSession.objects.create(
                student=self.student,
                session=session,
                is_approved=False
            )
            
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['requests']), 10)  # First page should have 10 items
        
        response = self.client.get(f"{self.url}?page=2")
        self.assertEqual(len(response.context['requests']), 2)  # Second page should have 2 items
