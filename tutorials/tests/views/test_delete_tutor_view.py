from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Tutor

class DeleteStudentViewTestCase(TestCase):
    """Test of the delete student view"""
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')

        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.url = reverse('delete_tutor', kwargs={'tutor_id': self.tutor.pk})

    def test_delete_tutor_url(self):
        self.assertEqual(self.url, f'/list-tutors/tutor/{self.tutor.pk}/delete-tutor/')

    def test_delete_tutor_authenticated_admin_user(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('list_tutors'))
        with self.assertRaises(Tutor.DoesNotExist):
            Tutor.objects.get(pk=self.tutor.pk)
            
    def test_delete_tutor_unauthenticated_student_user(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_delete_tutor_unauthenticated_tutor_user(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_delete_tutor_no_login(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('log_in'), response.url)

    def test_delete_tutor_non_existing_student(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        non_existing_url = reverse('tutor_detail', kwargs={'tutor_id': 9999})
        response = self.client.post(non_existing_url)
        self.assertEqual(response.status_code, 404)
