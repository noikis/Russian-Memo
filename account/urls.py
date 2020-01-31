from django.urls import path, include
from django.contrib.auth.views import LoginView

from .views import (StudentSignUpView, logout_view,
                    login_view, dashboard, TeacherSignUpView)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard', dashboard, name="dashboard"),
    path('student_registration/', StudentSignUpView.as_view(),
         name='student_registration'),
    path('teacher_registration/', TeacherSignUpView.as_view(),
         name='teacher_registration'),
]
