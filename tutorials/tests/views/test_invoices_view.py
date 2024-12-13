from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, StudentSession, Session, TutorSession, Tutor, ProgrammingLanguage, Invoice

class InvoicesViewTestCase(TestCase):
    """Tests of the invoices view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('invoices')
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')
        
        # Create test data
        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        
        self.language = ProgrammingLanguage.objects.create(name='Python')
        self.session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            session=self.session
        )
        
        self.student_session = StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session
        )

        self.invoice = Invoice.objects.create(
            session=self.student_session
        )

    def test_invoices_url(self):
        self.assertEqual(self.url, '/invoices/')

    def test_get_invoices_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_invoices_redirects_when_not_admin(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_get_invoices_for_admin(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices.html')
        
        # Check context data
        self.assertIn('invoices', response.context)
        invoices = response.context['invoices']
        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices[0], self.invoice)

    def test_invoices_pagination(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices.html')
        invoices = response.context['invoices']
        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices.number, 1)
        self.assertEqual(invoices.paginator.num_pages, 1)
