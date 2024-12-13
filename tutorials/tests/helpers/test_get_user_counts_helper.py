from django.test import TestCase
from tutorials.helpers import get_user_counts
from tutorials.models import User

class TestGetUserCounts(TestCase):
    """Tests for the get_user_counts helper function."""

    def setUp(self):
        User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="password123",
            role=User.Roles.STUDENT
        )
        User.objects.create_user(
            username="tutor1",
            email="tutor1@example.com",
            password="password123",
            role=User.Roles.TUTOR
        )
        User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="password123",
            role=User.Roles.ADMIN
        )

    def test_user_counts(self):
        """Check that the user counts are correct."""
        counts = get_user_counts()
        self.assertEqual(counts['total_users'], 3)
        self.assertEqual(counts['student_count'], 1)
        self.assertEqual(counts['tutor_count'], 1)

    def test_empty_user_counts(self):
        """Check counts when no users exist."""
        User.objects.all().delete()
        counts = get_user_counts()
        self.assertEqual(counts['total_users'], 0)
        self.assertEqual(counts['student_count'], 0)
        self.assertEqual(counts['tutor_count'], 0)

    def test_multiple_users_same_role(self):
        """Check counts with multiple users of the same role."""
        User.objects.create_user(
            username="student2",
            email="student2@example.com",
            password="password123",
            role=User.Roles.STUDENT
        )
        User.objects.create_user(
            username="student3",
            email="student3@example.com",
            password="password123",
            role=User.Roles.STUDENT
        )
        counts = get_user_counts()
        self.assertEqual(counts['total_users'], 5)
        self.assertEqual(counts['student_count'], 3)
        self.assertEqual(counts['tutor_count'], 1)

