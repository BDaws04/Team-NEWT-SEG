"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.LogInView.as_view(), name='log_in'),
    path('logout/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('signup/', views.SignUpView.as_view(), name='sign_up'),
    path('list-students/', views.list_students, name='list_students'),
    path('list-students/student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('list-students/student/<int:student_id>/delete-student/', views.delete_student, name='delete_student'),
    path('list-tutors/', views.list_tutors, name='list_tutors'),
    path('list-tutors/tutor/<int:tutor_id>/', views.tutor_detail, name='tutor_detail'),
    path('list-tutors/tutor/<int:tutor_id>/delete-tutor/', views.delete_tutor, name='delete_tutor'),
    path('tutor-sessions/<int:pk>/', views.tutor_session_detail, name='tutor_session_detail'),
    path('tutor-sessions/', views.tutor_sessions_list, name='tutor_sessions_list'),
    path('student-sessions/', views.student_sessions, name='student_sessions'),
    path('student-sessions/send-invoice/<int:session_id>/', views.send_invoice, name='send_invoice'),
    path('student-sessions/remove-session/<int:session_id>/', views.remove_session, name='remove_session'),
    path('request-session/', views.request_session, name='request_session'),
    path('pending-requests/', views.list_pending_requests, name='pending_requests'),
    path('invoices/', views.invoices, name='invoices'),
    path('available-tutors/<int:request_id>/', views.available_tutors, name='available_tutors'),
    path('available-tutors/<int:request_id>/approve-session/<int:tutor_session_id>/', views.approve_session, name='approve_session'),
    path('student-pending-payments/', views.student_pending_payments, name='student_pending_payments'),
    path('organised-sessions/', views.organised_sessions, name='organised_sessions'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)