from django.test import TestCase
from django import forms
from tutorials.forms import NewPasswordMixin

class NewPasswordMixinTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "new_password": "Password123",
            "password_confirmation": "Password123"
        }
        self.invalid_data_mismatch = {
            "new_password": "Password123",
            "password_confirmation": "Mismatch123"
        }
        self.invalid_data_weak_password = {
            "new_password": "password",
            "password_confirmation": "password"
        }

    def test_valid_password(self):
        """Test form with valid password and confirmation."""
        form = NewPasswordMixin(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["new_password"], "Password123")

    def test_password_mismatch(self):
        """Test form with mismatched password and confirmation."""
        form = NewPasswordMixin(data=self.invalid_data_mismatch)
        self.assertFalse(form.is_valid())
        self.assertIn("password_confirmation", form.errors)
        self.assertEqual(form.errors["password_confirmation"][0], "Confirmation does not match password.")

    def test_weak_password(self):
        """Test form with weak password not meeting validation criteria."""
        form = NewPasswordMixin(data=self.invalid_data_weak_password)
        self.assertFalse(form.is_valid())
        self.assertIn("new_password", form.errors)
        self.assertEqual(
            form.errors["new_password"][0],
            "Password must contain an uppercase character, a lowercase character and a number"
        )

    def test_empty_password(self):
        """Test form with empty password fields."""
        form = NewPasswordMixin(data={"new_password": "", "password_confirmation": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("new_password", form.errors)
        self.assertIn("password_confirmation", form.errors)

    def test_partial_password_input(self):
        """Test form with only one password field provided."""
        form = NewPasswordMixin(data={"new_password": "Password123", "password_confirmation": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("password_confirmation", form.errors)
