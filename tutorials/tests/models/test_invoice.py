from django.test import TestCase
from django.utils.timezone import now, timedelta
from tutorials.models import Invoice, StudentSession, TutorSession, Session, Student, Tutor, ProgrammingLanguage, User
from decimal import Decimal


class InvoiceTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpass',
            role='STUDENT'
        )
        self.tutor_user = User.objects.create_user(
            username='tutor1',
            email='tutor1@example.com',
            password='testpass',
            role='TUTOR'
        )

        # Create related objects for the session
        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.language = ProgrammingLanguage.objects.create(name='Python')
        self.session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=1,
            start_day=now().date(),
            end_day=now().date() + timedelta(weeks=12)
        )
        self.tutor_session = TutorSession.objects.create(tutor=self.tutor, session=self.session)
        self.student_session = StudentSession.objects.create(student=self.student, tutor_session=self.tutor_session)

    def test_invoice_creation_defaults(self):
        # Create an Invoice
        invoice = Invoice.objects.create(session=self.student_session)

        # Test default values
        self.assertEqual(invoice.amount, Decimal('30.00'))
        self.assertEqual(invoice.payment_status, 'PENDING')
        self.assertEqual(invoice.due_date, now().date() + timedelta(days=30))

    def test_invoice_string_representation(self):
        # Create an Invoice
        invoice = Invoice.objects.create(session=self.student_session)

        # Expected string representation
        expected_str = f"Invoice #{invoice.id} - {self.student_user.get_full_name()} - PENDING"
        self.assertEqual(str(invoice), expected_str)

    def test_invoice_amount_for_different_durations(self):
        # Test with duration_hours = 1
        self.session.duration_hours = 1
        self.session.save()
        invoice = Invoice.objects.create(session=self.student_session)
        self.assertEqual(invoice.amount, Decimal('30.00'))

        # Test with duration_hours = 2
        self.session.duration_hours = 2
        self.session.save()
        invoice = Invoice.objects.create(session=self.student_session)
        self.assertEqual(invoice.amount, Decimal('50.00'))

    def test_mark_as_paid(self):
        # Create an Invoice
        invoice = Invoice.objects.create(session=self.student_session)

        # Mark it as paid
        invoice.mark_as_paid()

        # Test payment status and payment_date
        self.assertEqual(invoice.payment_status, 'PAID')
        self.assertEqual(invoice.payment_date, now().date())

    def test_invoice_due_date_if_not_set(self):
        # Create an Invoice without a due_date
        invoice = Invoice.objects.create(session=self.student_session, due_date=None)

        # Check if due_date is automatically set
        self.assertIsNotNone(invoice.due_date)
        self.assertEqual(invoice.due_date, now().date() + timedelta(days=30))
