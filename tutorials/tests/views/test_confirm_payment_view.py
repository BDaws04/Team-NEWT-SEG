from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, StudentSession, Session, TutorSession, Tutor, ProgrammingLanguage, Invoice

class ConfirmPaymentViewTestCase(TestCase):
    """Tests of the confirm payment view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
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
        
        self.url = reverse('confirm_payment', kwargs={'invoice_id': self.invoice.id})

    def test_confirm_payment_url(self):
        self.assertEqual(self.url, f'/student-pending-payments/confirm-payment/{self.invoice.id}/')

    def test_confirm_payment_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_confirm_payment_redirects_when_not_student(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_successful_payment_confirmation(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        
        # Verify redirect
        self.assertRedirects(response, reverse('student_pending_payments'), status_code=302, target_status_code=200)
        
        # Refresh invoice from database
        self.invoice.refresh_from_db()
        self.student_session.refresh_from_db()
        
        # Verify status updates
        self.assertEqual(self.invoice.payment_status, 'PAID')
        self.assertEqual(self.student_session.status, 'Approved')
