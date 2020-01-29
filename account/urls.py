from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView


from .views import StudentSignUpView, logout_view, login_view, dashboard

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard', dashboard, name="dashboard"),
    path('registration/', StudentSignUpView.as_view(),
         name='student_registration'),
]
