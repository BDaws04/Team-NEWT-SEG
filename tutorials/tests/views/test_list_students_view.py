from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class ListStudentsViewTestCase(TestCase):
    """Test of the list students view"""
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]
    
    def setUp(self):
        self.url = reverse('list_students')
        self.student_user_1 = User.objects.get(username='@johndoe')
        self.student_user_2 = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')
        
    def test_list_students_url(self):
        self.assertEqual(self.url,'/list_students/')
        
    def test_list_students_authenticated_user(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_students.html')
        
        students = response.context['students']
        self.assertIn(self.student_user_1, students)
        self.assertIn(self.student_user_2, students)
        self.assertNotIn(self.tutor_user, students)
        
    def test_list_students_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.login_url = reverse('log_in')
        self.assertIn(self.login_url, response.url)
