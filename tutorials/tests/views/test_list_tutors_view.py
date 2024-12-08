from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Tutor

class ListTutorViewTestCase(TestCase):
    """Test of the list students view"""
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]
    
    def setUp(self):
        self.url = reverse('list_tutors')
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')

        Tutor.objects.create(user=self.tutor_user)
        
    def test_list_tutors_url(self):
        self.assertEqual(self.url,'/list-tutors/')
        
    def test_list_tutors_authenticated_admin_user(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_tutors.html')

        tutors = response.context['tutors']
        self.assertIn(self.tutor_user, [tutor.user for tutor in tutors])
        self.assertNotIn(self.admin_user, [tutor.user for tutor in tutors])
        self.assertNotIn(self.student_user, [tutor.user for tutor in tutors])
        
    def test_list_tutors_unauthenticated_student_user(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_list_tutors_unauthenticated_tutor_user(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

    def test_list_tutors_no_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('log_in'), response.url)

    def test_list_tutors_pagination(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_tutors.html')
        tutors = response.context['tutors']
        self.assertEqual(len(tutors), 1)
        self.assertEqual(tutors.number, 1)
        self.assertEqual(tutors.paginator.num_pages, 1)
