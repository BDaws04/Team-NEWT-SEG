from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student

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

        self.student = Student.objects.create(user=self.student_user)
        self.url = reverse('delete_student', kwargs={'student_id': self.student.pk})

    def test_delete_student_url(self):
        self.assertEqual(self.url, f'/list-students/student/{self.student.pk}/delete-student/')

    def test_delete_student_authenticated_admin_user(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('list_students'))
        with self.assertRaises(Student.DoesNotExist):
            Student.objects.get(pk=self.student.pk)
            
    def test_delete_student_unauthenticated_student_user(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_delete_student_unauthenticated_tutor_user(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_delete_student_no_login(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('log_in'), response.url)

    def test_delete_student_non_existing_student(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        non_existing_url = reverse('student_detail', kwargs={'student_id': 9999})
        response = self.client.post(non_existing_url)
        self.assertEqual(response.status_code, 404)

    def test_delete_student_non_existing_student_correct_url(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        non_existing_url = reverse('delete_student', kwargs={'student_id': 9999})
        response = self.client.post(non_existing_url)
        self.assertEqual(response.status_code, 404)
