"""Tests of the approve session view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Tutor, Session, TutorSession, RequestedStudentSession, ProgrammingLanguage, StudentSession

class ApproveSessionViewTestCase(TestCase):
    """Tests of the approve session view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')
        
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
        self.requested_session = RequestedStudentSession.objects.create(
            student=self.student,
            session=self.session
        )
        
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            session=self.session
        )
        
        
        self.url = reverse('approve_session', kwargs={
            'request_id': self.requested_session.id,
            'tutor_session_id': self.tutor_session.id
        })

    def test_approve_session_url(self):
        self.assertEqual(self.url, f'/available-tutors/{self.requested_session.id}/approve-session/{self.tutor_session.id}/')

    def test_get_approve_session_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_approve_session_redirects_when_not_admin(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_approve_session_with_invalid_request_id(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        url = reverse('approve_session', kwargs={
            'request_id': 99999,
            'tutor_session_id': self.tutor_session.id
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_approve_session_with_invalid_tutor_session_id(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        url = reverse('approve_session', kwargs={
            'request_id': self.requested_session.id,
            'tutor_session_id': 99999
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_successful_session_approval(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        before_count = StudentSession.objects.count()
        response = self.client.post(self.url)
        after_count = StudentSession.objects.count()
        
        self.assertEqual(after_count, before_count + 1)
        self.assertRedirects(response, reverse('pending_requests'), status_code=302, target_status_code=200)
        
        # Verify the requested session was deleted
        with self.assertRaises(RequestedStudentSession.DoesNotExist):
            RequestedStudentSession.objects.get(id=self.requested_session.id)
            
        # Verify student session was created correctly
        student_session = StudentSession.objects.latest('id')
        self.assertEqual(student_session.student, self.student)
        self.assertEqual(student_session.tutor_session, self.tutor_session)
        self.assertFalse(student_session.tutor_session.session.is_available)
