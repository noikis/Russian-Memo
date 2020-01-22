from django.urls import path
from .views import login_view, register_student, logout

urlpatterns = [
    path('login/',  login_view, name="login"),
    path('register/',  register_student, name="register_student"),
    path('logout/',  logout, name="logout"),

]
