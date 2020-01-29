from django.contrib import admin
from django.urls import path, include

from .views import index

app_name = 'main'
name_space = 'main'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('', index,  name='home'),
]
