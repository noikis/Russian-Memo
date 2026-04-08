from django.urls import path, include
from django.contrib.auth.views import LoginView

from .views import (StudentSignUpView, TeacherSignUpView, logout,
                    login, dashboard, TelegramAuthView, TelegramWebAppAuthView, TelegramMiniAppAuthPageView,
                    vk_oauth_start, vk_oauth_callback)

app_name = 'account'

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', dashboard, name="dashboard"),
    path('student_registration/', StudentSignUpView.as_view(),
         name='student_registration'),
    path('teacher_registration/', TeacherSignUpView.as_view(),
         name='teacher_registration'),
    path('telegram_auth/', TelegramAuthView.as_view(), name='telegram_auth'),
    path('telegram_webapp_auth/', TelegramWebAppAuthView.as_view(), name='telegram_webapp_auth'),
    path('tg_auth/', TelegramMiniAppAuthPageView.as_view(), name='telegram_mini_app_auth_page'),
    path('vk_oauth_start/', vk_oauth_start, name='vk_oauth_start'),
    path('vk_oauth_callback/', vk_oauth_callback, name='vk_oauth_callback'),
]
