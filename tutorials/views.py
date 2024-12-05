from django.http import Http404, HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from tutorials.models import Student, Tutor, TutorSession
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .helpers import get_user_counts
from django.contrib.auth import get_user_model
from tutorials.forms import StudentSessionForm
from tutorials.models import ProgrammingLanguage, RequestedStudentSession
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError

User = get_user_model()

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    context = {'user': current_user}

    if current_user.role == 'STUDENT':

        form = StudentSessionForm()

        if request.method == 'POST':
            form = StudentSessionForm(request.POST)
            if form.is_valid():
                # Save the session object
                session = form.save()

                # Get the related student profile
                student = current_user.student_profile

                print(f"Student: {student}")

                # Create the RequestedStudentSession instance
                requested_session = RequestedStudentSession(
                    student=student,
                    session=session,
                )

                try:
                     requested_session.full_clean()  # Validate the model
                     requested_session.save()  # Save the object
                     print(f"Requested session saved with ID: {requested_session.id}")
                except ValidationError as e:
                    print(f"Validation error: {e}")
                except Exception as e:
                    print(f"Error saving requested session: {e}")

                context['message'] = 'Session request has been received!'
                form = None  # Remove the form after successful submission
            else:
                context['message'] = 'There was an error with your submission.'

        # Ensure form is always in the context, either for initial render or after errors
        context['form'] = form

        return render(request, 'student_dashboard.html', context)

    elif current_user.role == 'TUTOR':
        return render(request, 'tutor_dashboard.html', context)

    elif current_user.role == 'ADMIN':
        return render(request, 'admin_dashboard.html', context)

    else:
        return render(request, 'dashboard.html', context)



@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()



    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    
@login_required
def list_students(request):
    """Display a paginated list of all users who are students."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')  # Redirect non-admin users to their dashboard

    # Get all students
    students_list = Student.objects.all()
    
    # Implement pagination with 10 students per page
    paginator = Paginator(students_list, 10)  # 10 students per page
    page_number = request.GET.get('page')  # Get the current page number from the query params
    students = paginator.get_page(page_number)  # Get the students for the current page

    # Render the template with paginated students
    return render(request, 'list_students.html', {'students': students})

@login_required
def list_students_no_navbar(request):
    """Display all users who are students."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    students = Student.objects.all()
    return render(request, 'list_students_no_navbar.html', {'students': students})

@login_required
def student_detail(request, student_id):
    """Display the details of a specific student."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    try:
        student = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        raise Http404(f"Could not find student with primary key {student_id}")
    else:
        context = {'student': student, 'student_id': student_id}
        return render(request, 'student_detail.html', context)

@login_required
def delete_student(request, student_id):
    """Delete the records of a specific student."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    try:
        student = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        raise Http404(f"Count not find student with primary key {student_id}")
    else:
        if request.method == "POST":
            student.delete()
            path = reverse('list_students')
            return HttpResponseRedirect(path)
        
@login_required
def list_tutors(request):
    """Display all users who are tutors."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    tutors = Tutor.objects.all()
    return render(request, 'list_tutors.html', {'tutors': tutors})

@login_required
def tutor_detail(request, tutor_id):
    """Display the details of a specific tutor."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    try:
        tutor = Tutor.objects.get(pk=tutor_id)
    except Tutor.DoesNotExist:
        raise Http404(f"Count not find tutor with primary key {tutor_id}")
    else:
        context = {'tutor': tutor, 'tutor_id': tutor_id}
        return render(request, 'tutor_detail.html', context)
    
@login_required
def delete_tutor(request, tutor_id):
    """Delete the records of a specific tutor."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    try:
        tutor = Tutor.objects.get(pk=tutor_id)
    except Student.DoesNotExist:
        raise Http404(f"Count not find student with primary key {tutor_id}")
    else:
        if request.method == "POST":
            tutor.delete()
            path = reverse('list_tutors')
            return HttpResponseRedirect(path)

@login_required
def tutor_sessions_list(request):
    tutors = Tutor.objects.filter(tutor_sessions__isnull=False).distinct()  # Only include tutors with sessions
    return render(request, 'tutor_sessions_list.html', {'tutors': tutors})

@login_required
def tutor_session_detail(request, pk):
    tutor_session = get_object_or_404(TutorSession, id=pk)  # Use `pk` instead of `session_id`
    return render(request, 'tutor_session_detail.html', {'session': tutor_session})