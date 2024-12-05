from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Admin

class AdminModelTestCase(TestCase):
    """Unit tests for the Admin model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.admin = Admin.objects.create(user=self.user)

    def test_valid_admin(self):
        self._assert_admin_is_valid()

    def test_str_method(self):
        self.assertEqual(str(self.admin), f'Admin: {self.user.get_full_name()}')

    def _assert_admin_is_valid(self):
        try:
            self.admin.full_clean()
        except (ValidationError):
            self.fail('Test tutor should be valid')

    def _assert_admin_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.admin.full_clean() 
