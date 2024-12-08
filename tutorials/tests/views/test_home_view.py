"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Tutor, Admin

class HomeViewTestCase(TestCase):
    """Tests of the home view."""

    fixtures = ['tutorials/tests/fixtures/default_user.json',
                'tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(username='@johndoe')

    def test_home_url(self):
        self.assertEqual(self.url,'/')

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirects_when_logged_in_as_student(self):
        """Test that logged in students are redirected to their dashboard."""
        user = User.objects.get(username='@janedoe')
        Student.objects.create(user=user)
        
        self.client.login(username=user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

    def test_get_home_redirects_when_logged_in_as_tutor(self):
        """Test that logged in tutors are redirected to their dashboard."""
        user = User.objects.get(username='@petrapickles')
        Tutor.objects.create(user=user)

        self.client.login(username=user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_dashboard.html')

    def test_get_home_redirects_when_logged_in_as_admin(self):
        """Test that logged in admins are redirected to their dashboard."""
        user = User.objects.get(username='@johndoe')
        Admin.objects.create(user=user)

        self.client.login(username=user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
