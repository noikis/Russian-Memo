from django.urls import path, include
from django.contrib.auth.views import LoginView

from .views import (StudentSignUpView, TeacherSignUpView, logout,
                    login, dashboard, )

app_name = 'account'

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', dashboard, name="dashboard"),
    path('student_registration/', StudentSignUpView.as_view(),
         name='student_registration'),
    path('teacher_registration/', TeacherSignUpView.as_view(),
         name='teacher_registration'),
]
