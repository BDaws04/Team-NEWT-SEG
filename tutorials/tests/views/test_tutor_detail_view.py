from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Tutor

class TutorDetailViewTestCase(TestCase):
    """Test of the student detail view"""
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')

        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.url = reverse('tutor_detail', kwargs={'tutor_id': self.tutor.pk})

    def test_tutor_detail_url(self):
        self.assertEqual(self.url, f'/list-tutors/tutor/{self.tutor.pk}/')
    
    def test_tutor_detail_authenticated_admin_user(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_detail.html')

        self.assertEqual(response.context['tutor'], self.tutor)
        self.assertEqual(response.context['tutor_id'], self.tutor.pk)
        
    def test_tutor_detail_unauthenticated_student_user(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_tutor_detail_unauthenticated_tutor_user(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_tutor_detail_no_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('log_in'), response.url)

    def test_tutor_detail_non_existing_student(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        non_existing_url = reverse('tutor_detail', kwargs={'tutor_id': 9999})
        response = self.client.get(non_existing_url)
        self.assertEqual(response.status_code, 404)
        