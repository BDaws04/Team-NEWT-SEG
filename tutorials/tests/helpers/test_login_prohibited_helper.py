from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from tutorials.models import User
from tutorials.helpers import login_prohibited

class TestLoginProhibitedDecorator(TestCase):
    """Tests for the login_prohibited decorator."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role=User.Roles.STUDENT
        )

    def test_redirect_if_logged_in(self):
        """Check that the user is redirected if logged in."""
        request = self.factory.get('/')
        request.user = self.user

        @login_prohibited
        def mock_view(request):
            return "Access granted"

        response = mock_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_access_if_anonymous(self):
        """Check that an anonymous user can access the view."""
        request = self.factory.get('/')
        request.user = AnonymousUser()

        @login_prohibited
        def mock_view(request):
            return "Access granted"

        response = mock_view(request)
        self.assertEqual(response, "Access granted")

    def test_post_request_if_logged_in(self):
        """Check that POST requests are also redirected if logged in."""
        request = self.factory.post('/')
        request.user = self.user

        @login_prohibited
        def mock_view(request):
            return "Access granted"

        response = mock_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

