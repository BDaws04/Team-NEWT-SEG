from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Admin, Student, Tutor

class StudentDetailViewTestCase(TestCase):
    """Test of the student detail view"""
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')

        self.student = Student.objects.create(user=self.student_user)
        self.url = reverse('student_detail', kwargs={'student_id': self.student.pk})

    def test_student_detail_url(self):
        self.assertEqual(self.url, f'/list_students/student/{self.student.pk}/')
    
    def test_list_students_authenticated_admin_user(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_detail.html')

        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['student_id'], self.student.pk)
        
    def test_list_students_unauthenticated_student_user(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_list_students_unauthenticated_tutor_user(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_student_detail_no_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('log_in'), response.url)

    def test_student_detail_non_existing_student(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        non_existing_url = reverse('student_detail', kwargs={'student_id': 9999})
        response = self.client.get(non_existing_url)
        self.assertEqual(response.status_code, 404)
        