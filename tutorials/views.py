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
from tutorials.models import Student, Tutor, TutorSession, Invoice, StudentSession
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from tutorials.forms import SessionForm
from tutorials.models import ProgrammingLanguage, RequestedStudentSession
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@login_required
def approve_session(request, request_id):
    return HttpResponseForbidden("You do not have permission to access this page.")

@login_required
def request_session(request):
    """Display the form to request a new session."""

    current_user = request.user
    context = {'user': current_user}

    if current_user.role == 'STUDENT':

        form = SessionForm()

        if request.method == 'POST':
            form = SessionForm(request.POST)
            if form.is_valid():
                # Save the session object
                session = form.save()

                # Get the related student profile
                student = Student.objects.get(user=current_user)

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
                    context['message'] = 'Session request has been received!'
                    form = None  # Clear the form after successful submission
                except ValidationError as e:
                    print(f"Validation error: {e}")
                    context['message'] = 'There was a validation error with your request.'
                # except Exception as e:
                #     print(f"Error saving requested session: {e}")
                #     context['message'] = 'There was an error with your submission.'

            else:
                context['message'] = 'There was an error with your submission.'

        context['form'] = form
        return render(request, 'request_session.html', context)

    elif current_user.role == 'TUTOR':

        form = SessionForm()

        if request.method == 'POST':
            form = SessionForm(request.POST)
            if form.is_valid():
                # Save the session objec
                session = form.save()

                # Get the related tutor profile
                tutor = Tutor.objects.get(user=current_user)

                print(f"Tutor: {tutor}")

                # Assign the tutor to the session
                tutor_session = TutorSession.objects.create(
                    tutor=tutor,
                    session=session,
                )

                try:
                    tutor_session.full_clean()  # Validate the model
                    tutor_session.save()  # Save the object
                    print(f"Session saved with ID: {tutor_session.id}")
                    context['message'] = 'Session request has been received!'
                    form = None  # Clear the form after successful submission
                except ValidationError as e:
                    print(f"Validation error: {e}")
                    context['message'] = 'There was a validation error with your request.'
                except Exception as e:
                    print(f"Error saving session: {e}")
                    context['message'] = 'There was an error with your submission.'

            else:
                context['message'] = 'There was an error with your submission.'

        context['form'] = form
        return render(request, 'request_session.html', context)
        
    else:
        return redirect('dashboard')

        

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    context = {'user': current_user}

    if current_user.role == 'STUDENT':
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
def list_pending_requests(request):
    """Display a paginated and filterable list of all pending session requests."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')

    # Fetch filter parameters
    level_filter = request.GET.get('level')
    year_filter = request.GET.get('year')
    language_filter = request.GET.get('language')

    # Base queryset for pending requests
    pending_requests = RequestedStudentSession.objects.filter(is_approved=False)

    # Apply filters
    if level_filter and level_filter != "All Levels":
        pending_requests = pending_requests.filter(session__level=level_filter)
    if year_filter and year_filter != "All Years":
        pending_requests = pending_requests.filter(session__year=year_filter)
    if language_filter and language_filter != "All Programming Languages":
        pending_requests = pending_requests.filter(session__programming_language__name=language_filter)

    # Pagination
    paginator = Paginator(pending_requests, 10)
    page_number = request.GET.get('page')
    requests = paginator.get_page(page_number)

    # Fetch distinct levels, years, and programming languages for filter options
    levels = RequestedStudentSession.objects.values_list('session__level', flat=True).distinct()
    years = RequestedStudentSession.objects.values_list('session__year', flat=True).distinct()
    languages = RequestedStudentSession.objects.values_list('session__programming_language__name', flat=True).distinct()

    # Context
    context = {
        'requests': requests,
        'levels': sorted(set(levels)),  # Ensures levels are unique and sorted
        'years': sorted(set(years)),  # Ensures years are unique and sorted
        'languages': sorted(set(languages)),  # Ensures languages are unique and sorted
        'level_filter': level_filter,
        'year_filter': year_filter,
        'language_filter': language_filter,
    }

    return render(request, 'pending_requests.html', context)

    
@login_required
def list_tutors(request):
    """Display a paginated list of all users who are students."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    tutor_list = Tutor.objects.all()
    
    paginator = Paginator(tutor_list, 10)
    page_number = request.GET.get('page')
    tutors = paginator.get_page(page_number)

    return render(request, 'list_tutors.html', {'tutors': tutors})
    
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
def student_detail(request, student_id):
    """Display the details of a specific student."""
    current_user = request.user

    if current_user.role != 'ADMIN' and current_user.role != 'TUTOR':
        return redirect('dashboard')  # Redirect non-admin/tutors to their dashboard

    try:
        student = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        raise Http404(f"Could not find student with primary key {student_id}")

    return render(request, 'student_detail.html', {'student': student})

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
    except Tutor.DoesNotExist:
        raise Http404(f"Count not find tutor with primary key {tutor_id}")
    else:
        if request.method == "POST":
            tutor.delete()
            path = reverse('list_tutors')
            return HttpResponseRedirect(path)

@login_required
def tutor_sessions_list(request):
    """Display a paginated list of all tutors with sessions."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    tutors = Tutor.objects.filter(tutor_sessions__isnull=False).distinct()  # Only include tutors with sessions
    return render(request, 'tutor_sessions_list.html', {'tutors': tutors})

@login_required
def tutor_session_detail(request, pk):
    """Display the details of a specific tutor session."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    tutor_session = get_object_or_404(TutorSession, id=pk)  # Use `pk` instead of `session_id`
    return render(request, 'tutor_session_detail.html', {'session': tutor_session}) 

@login_required
def student_sessions(request):
    """Display all sessions for a specific student."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    session_list = StudentSession.objects.all()

    paginator = Paginator(session_list, 10)
    page_number = request.GET.get('page')
    sessions = paginator.get_page(page_number)
    return render(request, 'student_sessions.html', {'sessions': sessions})

@login_required
def send_invoice(request, session_id):
    """Send an invoice for a specific session."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    try:
        student_session = StudentSession.objects.get(pk=session_id)
        
        student_session.status = 'Payment Pending'
        try:
            student_session.save()
        except ValueError as e:
            print(f"Error saving StudentSession: {e}")
            messages.error(request, str(e))
            return redirect('student_sessions')
        
        invoice = Invoice.objects.create(
            session=student_session,
        )
        
        invoice.save()
        
        return redirect('student_sessions')
        
    except StudentSession.DoesNotExist:
        raise Http404(f"Could not find student session with primary key {session_id}")

@login_required
def remove_session(request, session_id):
    """Remove a specific session."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    try:
        student_session = StudentSession.objects.get(pk=session_id)
    except StudentSession.DoesNotExist:
        raise Http404(f"Could not find student session with primary key {session_id}")
    else:
        student_session.delete()
        path = reverse('student_sessions')
        return HttpResponseRedirect(path)

@login_required
def invoices(request):
    """Display all invoices for student lessons with tutors."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    invoices = Invoice.objects.all()
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)
    return render(request, 'invoices.html', {'invoices': invoices})
 
@login_required
def available_tutors(request, request_id):
    """Display all available tutors for a specific session request."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    try:
        requested_session = RequestedStudentSession.objects.get(pk=request_id)
    except RequestedStudentSession.DoesNotExist:
        raise Http404(f"Could not find session request with primary key {request_id}")
    else:
        requested_session.save()
        tutors = requested_session.available_tutor_sessions.all()
        print(f"Available tutors: {tutors}")
        paginator = Paginator(tutors, 10)
        page_number = request.GET.get('page')
        tutors = paginator.get_page(page_number)                  
        context = {'tutors': tutors, 'request_id': request_id}
        return render(request, 'available_tutors.html', context)
    
@login_required
def approve_session(request, request_id, tutor_session_id):
    """Approve a specific session request."""
    current_user = request.user
    if current_user.role != 'ADMIN':
        return redirect('dashboard')
    try:
        requested_session = RequestedStudentSession.objects.get(pk=request_id)
    except RequestedStudentSession.DoesNotExist:
        raise Http404(f"Could not find session request with primary key {request_id}")
    else:
        if request.method == "POST":
            try:
                tutor_session = TutorSession.objects.get(pk=tutor_session_id)
            except TutorSession.DoesNotExist:
                raise Http404(f"Could not find tutor session with primary key {tutor_session_id}")
            else:
                tutor_session.session.is_available = True
                tutor_session.session.save()
                StudentSession.objects.create(
                    student=requested_session.student,
                    tutor_session=tutor_session,
                )

            requested_session.delete()
            path = reverse('pending_requests')
            return HttpResponseRedirect(path)
        
@login_required
def student_pending_payments(request):
    """Display all pending payments for student lessons with tutors."""
    current_user = request.user
    student = Student.objects.get(user=current_user)
    if current_user.role != 'STUDENT':
        return redirect('dashboard')
    pending_payments = Invoice.objects.filter(payment_status='PENDING', session__student=student)
    return render(request, 'student_pending_payment.html', {'pending_payments': pending_payments})

@login_required
def confirm_payment(request, invoice_id):
    """Confirm a specific payment."""
    current_user = request.user
    if current_user.role != 'STUDENT':
        return redirect('dashboard')
    invoice = Invoice.objects.get(pk=invoice_id)
    invoice.payment_status = 'PAID'
    invoice.session.status = 'Approved'
    invoice.session.save() # Need to save the student session after updating its status
    invoice.save()
    return redirect('student_pending_payments')

@login_required
def your_sessions(request):
    # Check if the user has a student profile
    try:
        student_profile = request.user.student_profile
    except AttributeError:
        raise Http404("You do not have a student profile.")

    # Fetch the sessions for the student
    student_sessions = StudentSession.objects.filter(student=student_profile)

    return render(request, 'your_sessions.html', {'student_sessions': student_sessions})

@login_required
def requested_sessions(request):
    # Filter requested sessions for the current student
    try:
        student_profile = request.user.student_profile
    except AttributeError:
        return render(request, 'requested_sessions.html', {'requested_sessions': []})

    requested_sessions = RequestedStudentSession.objects.filter(student=student_profile)
    return render(request, 'requested_sessions.html', {'requested_sessions': requested_sessions})

@login_required
def your_tutor_sessions(request):
    # Check if the user has a tutor profile
    try:
        tutor_profile = request.user.tutor_profile
    except AttributeError:
        raise Http404("You do not have a tutor profile.")

    # Fetch the sessions for the tutor
    tutor_sessions = TutorSession.objects.filter(tutor=tutor_profile)

    return render(request, 'your_tutor_sessions.html', {'tutor_sessions': tutor_sessions})

@login_required
def session_details(request, session_id):
    tutor_session = get_object_or_404(TutorSession, id=session_id)
    return render(request, 'session_details.html', {'tutor_session': tutor_session})