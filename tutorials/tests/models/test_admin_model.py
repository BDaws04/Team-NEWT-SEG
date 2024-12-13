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

    def test_user_must_exist(self):
        self.admin.user = None
        self._assert_admin_is_invalid()

    def test_str_method(self):
        expected = f'Admin: {self.user.full_name()}'
        self.assertEqual(str(self.admin), expected)

    def test_role_set_to_admin_on_save(self):
        user = User.objects.create(
            username='@newadmin',
            email='newadmin@example.com',
            first_name='New',
            last_name='Admin'
        )
        admin = Admin.objects.create(user=user)
        admin.save()
        self.assertEqual(admin.user.role, User.Roles.ADMIN)

    def test_role_updated_to_admin_if_different(self):
        user = User.objects.create(
            username='@newadmin2',
            email='newadmin2@example.com',
            first_name='New',
            last_name='Admin',
            role='STUDENT'
        )
        admin = Admin.objects.create(user=user)
        self.assertEqual(admin.user.role, User.Roles.ADMIN)

    def test_user_must_be_unique(self):
        with self.assertRaises(ValidationError):
            duplicate_admin = Admin(user=self.user)
            duplicate_admin.full_clean()

    def test_admin_creation_without_save(self):
        user = User.objects.create(
            username='@newadmin3',
            email='newadmin3@example.com',
            first_name='New',
            last_name='Admin'
        )
        admin = Admin(user=user)
        self._assert_admin_is_valid()

    def _assert_admin_is_valid(self):
        try:
            self.admin.full_clean()
        except ValidationError:
            self.fail('Test admin should be valid')

    def _assert_admin_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.admin.full_clean()
