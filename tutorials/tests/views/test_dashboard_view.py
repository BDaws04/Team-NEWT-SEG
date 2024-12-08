"""Tests of the dashboard view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Tutor

class DashboardViewTestCase(TestCase):
    """Tests of the dashboard view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('dashboard')
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')
        
        Student.objects.create(user=self.student_user)
        Tutor.objects.create(user=self.tutor_user)

    def test_dashboard_url(self):
        self.assertEqual(self.url,'/dashboard/')

    def test_get_dashboard_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url)

    def test_get_dashboard_for_student(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

    def test_get_dashboard_for_tutor(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_dashboard.html')

    def test_get_dashboard_for_admin(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
