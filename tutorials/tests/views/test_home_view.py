"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Tutor

class HomeViewTestCase(TestCase):
    """Tests of the home view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('home')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')
        self.admin_user = User.objects.get(username='@johndoe')
        
        Student.objects.create(user=self.student_user)
        Tutor.objects.create(user=self.tutor_user)

    def test_home_url(self):
        self.assertEqual(self.url, '/')

    def test_get_home_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirects_when_logged_in_as_student(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)
        
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(dashboard_response, 'student_dashboard.html')

    def test_get_home_redirects_when_logged_in_as_tutor(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)
        
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(dashboard_response, 'tutor_dashboard.html')

    def test_get_home_redirects_when_logged_in_as_admin(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)
        
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(dashboard_response, 'admin_dashboard.html')
