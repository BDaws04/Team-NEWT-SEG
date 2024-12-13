from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student

class ListStudentsViewTestCase(TestCase):
    """Test of the list students view"""
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]
    
    def setUp(self):
        self.url = reverse('list_students')
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')

        Student.objects.create(user=self.student_user)
        
    def test_list_students_url(self):
        self.assertEqual(self.url,'/list-students/')
        
    def test_list_students_authenticated_admin_user(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_students.html')

        students = response.context['students']
        self.assertIn(self.student_user, [student.user for student in students])
        self.assertNotIn(self.admin_user, [student.user for student in students])
        self.assertNotIn(self.tutor_user, [student.user for student in students])
        
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

    def test_list_students_no_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('log_in'), response.url)
    
    def test_list_students_pagination(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_students.html')
        students = response.context['students']
        self.assertEqual(len(students), 1)
        self.assertEqual(students.number, 1)
        self.assertEqual(students.paginator.num_pages, 1)

    def test_list_students_sort_order(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        
        # Test ascending sort order
        response = self.client.get(self.url + '?sort=asc')
        self.assertEqual(response.status_code, 200)
        students = response.context['students']
        self.assertEqual(len(students), 1)
        
        # Test descending sort order
        response = self.client.get(self.url + '?sort=desc')
        self.assertEqual(response.status_code, 200)
        students = response.context['students']
        self.assertEqual(len(students), 1)

    def test_list_students_multiple_pages(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        
        # Create 11 more students (12 total)
        for i in range(11):
            user = User.objects.create(
                username=f'@student{i}',
                first_name=f'Student{i}',
                last_name='Test',
                email=f'student{i}@example.org'
            )
            Student.objects.create(user=user)
            
        # Test first page
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['students']), 10)  # First page should have 10 items
        self.assertTrue(response.context['students'].has_next())
        self.assertFalse(response.context['students'].has_previous())
        
        # Test second page
        response = self.client.get(f"{self.url}?page=2")
        self.assertEqual(len(response.context['students']), 2)  # Second page should have 2 items
        self.assertFalse(response.context['students'].has_next())
        self.assertTrue(response.context['students'].has_previous())
        
        # Test invalid page
        response = self.client.get(f"{self.url}?page=999")
        self.assertEqual(len(response.context['students']), 2)  # Should show last page
