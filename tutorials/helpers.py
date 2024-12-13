from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import TutorSession

User = get_user_model()

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function


def get_user_counts():

    total_users = User.objects.count()
    student_count = User.objects.filter(role='STUDENT').count()
    tutor_count = User.objects.filter(role='TUTOR').count()
    admin_count = User.objects.filter(role='ADMIN').count()

    return {
        'total_users': total_users,
        'student_count': student_count,
        'tutor_count': tutor_count,
        'admin_count': admin_count,
    }

