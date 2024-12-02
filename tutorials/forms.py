"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Tutor, Student, ProgrammingLanguage, Session

from django import forms
from django.contrib.auth import authenticate

class StudentSessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            'programming_language',
            'level',
            'season',
            'year',
            'frequency',
            'duration_hours',
        ]

    programming_language = forms.ModelChoiceField(
        queryset=ProgrammingLanguage.objects.all(),
        required=True,
        label="Select the programming language",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    level = forms.ChoiceField(
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        required=True,
        label="Select the level",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    season = forms.ChoiceField(
        choices=Session.SEASONS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    year = forms.ChoiceField(
        choices=[(2024, '2024'), (2025, '2025'), (2026, '2026')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    frequency = forms.ChoiceField(
        choices=[('Weekly', 'Weekly'), ('Bi-Weekly', 'Bi-Weekly')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    duration_hours = forms.ChoiceField(
        choices=[(1, '1 Hour'), (2, '2 Hours')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['programming_language'].label = 'Programming Language'
        self.fields['level'].label = 'Level of Expertise'
        self.fields['season'].label = 'Season'
        self.fields['year'].label = 'Year'
        self.fields['frequency'].label = 'Session Frequency'
        self.fields['duration_hours'].label = 'Duration (Hours)'


class LogInForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    def get_user(self):
        """Authenticate user with the given credentials."""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user

class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    ROLE_CHOICES = [
        (User.Roles.STUDENT, 'Student'),
        (User.Roles.TUTOR, 'Tutor'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label="Select your role",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    expertise = forms.ModelMultipleChoiceField(
        queryset=ProgrammingLanguage.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Select programming languages you specialize in"
    )

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)

        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )

        role = self.cleaned_data.get('role')

        if role == User.Roles.TUTOR:
            tutor = Tutor(user=user)
            tutor.save()

            # Assign specialties to the tutor
            expertise = self.cleaned_data.get('expertise')
            if expertise:
                tutor.expertise.set(expertise)

        else:
            student = Student(user=user)
            student.save()
        
        user.role = role
        user.save()

        return user