from django.contrib import admin
from .models import User, Tutor, Student, Session, StudentSession, ProgrammingLanguage

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']

@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise_list')
    list_filter = ('expertise',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    filter_horizontal = ('expertise',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'enrollment_date']
    search_fields = ['user__username', 'user__email']
    list_filter = ['enrollment_date']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['programming_language', 'tutor', 'level','frequency', 'season', 'year']
    search_fields = ['programming_language__name', 'tutor__user__username', 'level','frequency', 'season', 'year']
    list_filter = ['level', 'season', 'year','frequency']


@admin.register(StudentSession)
class StudentSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'registered_at']
    search_fields = ['student__user__username', 'session__programming_language__name']
    list_filter = ['registered_at']
