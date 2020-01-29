from django.contrib import admin
from django.urls import path, include

from .views import StudentSignUpView

urlpatterns = [
    path('registration/', StudentSignUpView.as_view(),
         name='student_registration'),
]
