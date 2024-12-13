from django.contrib import admin
from .models import (
    Admin, User, Student, ProgrammingLanguage, Tutor, Session, TutorSession, RequestedStudentSession, StudentSession, Invoice
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email', 'first_name', 'last_name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'enrollment_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    filter_horizontal = ['previous_sessions']

@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ['user', 'expertise_list']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    filter_horizontal = ['expertise']

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ['user']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['programming_language', 'level', 'season', 'year', 'frequency', 'start_day', 'end_day', 'is_available']
    search_fields = ['programming_language__name', 'season', 'year']
    list_filter = ['level', 'season', 'year', 'frequency', 'is_available']

@admin.register(TutorSession)
class TutorSessionAdmin(admin.ModelAdmin):
    list_display = ['tutor', 'session', 'created_at']
    search_fields = ['tutor__user__username', 'session__programming_language__name']
    list_filter = ['created_at']

@admin.register(RequestedStudentSession)
class RequestedStudentSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'is_approved', 'requested_at']
    search_fields = ['student__user__username', 'session__programming_language__name']
    list_filter = ['is_approved', 'requested_at']
    filter_horizontal = ['available_tutor_sessions']

@admin.register(StudentSession)
class StudentSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'tutor_session', 'status', 'registered_at')
    search_fields = ('student__user__username', 'tutor_session__session__programming_language__name')
    list_filter = ('status',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['session', 'amount', 'created_at', 'payment_status']
    search_fields = ['session__student__user__username', 'session__tutor__user__username']
    list_filter = ['payment_status', 'created_at']

