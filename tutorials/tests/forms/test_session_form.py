from django.test import TestCase
from tutorials.models import ProgrammingLanguage, Session
from tutorials.forms import SessionForm
from datetime import datetime

class SessionFormTest(TestCase):
    def setUp(self):
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.valid_data = {
            "programming_language": self.language.id,
            "level": "beginner",
            "season": "Fall",
            "year": 2024,
            "frequency": "Weekly",
            "duration_hours": 2,
        }

    def test_valid_form(self):
        form = SessionForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_year(self):
        invalid_data = self.valid_data.copy()
        invalid_data["year"] = 2023 
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["year"][0], "Select a valid choice. 2023 is not one of the available choices.")

    def test_invalid_duration_hours(self):
        invalid_data = self.valid_data.copy()
        invalid_data["duration_hours"] = 0  
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["duration_hours"][0], "Select a valid choice. 0 is not one of the available choices.")

    def test_default_end_day(self):
        form = SessionForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        session = form.save()
        self.assertEqual(session.end_day, datetime(2024, 12, 13).date())
