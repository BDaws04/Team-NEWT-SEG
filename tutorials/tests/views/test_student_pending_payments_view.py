from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, StudentSession, Session, TutorSession, Tutor, ProgrammingLanguage, Invoice

class StudentPendingPaymentsViewTestCase(TestCase):
    """Tests of the student pending payments view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('student_pending_payments')
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
            tutor_session=self.tutor_session,
            status='Payment Pending'
        )

        self.invoice = Invoice.objects.create(
            session=self.student_session,
            payment_status='PENDING'
        )

    def test_student_pending_payments_url(self):
        self.assertEqual(self.url, '/student-pending-payments/')

    def test_get_student_pending_payments_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_student_pending_payments_redirects_when_not_student(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_get_student_pending_payments_for_student(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_pending_payment.html')
        
        # Check context data
        self.assertIn('pending_payments', response.context)
        pending_payments = response.context['pending_payments']
        self.assertEqual(len(pending_payments), 1)
        self.assertEqual(pending_payments[0], self.invoice)

    def test_student_pending_payments_shows_only_own_payments(self):
        # Create another student with pending payment
        other_student_user = User.objects.create_user(
            username='@otherstudent',
            password='Password123',
            role='STUDENT'
        )
        other_student = Student.objects.create(user=other_student_user)
        other_student_session = StudentSession.objects.create(
            student=other_student,
            tutor_session=self.tutor_session,
            status='Payment Pending'
        )
        other_invoice = Invoice.objects.create(
            session=other_student_session,
            payment_status='PENDING'
        )

        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        
        pending_payments = response.context['pending_payments']
        self.assertEqual(len(pending_payments), 1)
        self.assertEqual(pending_payments[0], self.invoice)
        self.assertNotIn(other_invoice, pending_payments)
