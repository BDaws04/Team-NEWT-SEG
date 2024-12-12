from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Student, Tutor, Session, TutorSession, StudentSession, Invoice, ProgrammingLanguage
from decimal import Decimal

class InvoiceModelTestCase(TestCase):
    """Unit tests for the Invoice model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.language = ProgrammingLanguage.objects.create(name='Python')
        self.session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        
        self.student_user = User.objects.get(username='@janedoe')
        self.student = Student.objects.create(user=self.student_user)
        
        self.tutor_user = User.objects.get(username='@petrapickles')
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            session=self.session
        )
        
        self.student_session = StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session
        )
        
        self.invoice = Invoice.objects.create(
            session=self.student_session,
            amount=Decimal('50.00')
        )

    def test_valid_invoice(self):
        self._assert_invoice_is_valid()

    def test_session_must_exist(self):
        self.invoice.session = None
        self._assert_invoice_is_invalid()

    def test_default_payment_status_is_pending(self):
        self.assertEqual(self.invoice.payment_status, 'PENDING')

    def test_str_method(self):
        expected = f"Invoice #{self.invoice.id} - {self.student_session.student.user.get_full_name()} - PENDING"
        self.assertEqual(str(self.invoice), expected)

    def test_valid_payment_status_choices(self):
        valid_statuses = ['PENDING', 'PAID', 'OVERDUE', 'CANCELLED']
        for status in valid_statuses:
            self.invoice.payment_status = status
            self._assert_invoice_is_valid()

    def test_invalid_payment_status(self):
        self.invoice.payment_status = 'INVALID'
        self._assert_invoice_is_invalid()

    def _assert_invoice_is_valid(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail('Test invoice should be valid')

    def _assert_invoice_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()
