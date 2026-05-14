from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import index
from words.views import cards

app_name = 'main'
name_space = 'main'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls', namespace='account',)),
    path('quiz/', include('quiz.urls', namespace='quiz',)),
    path('words/', include('words.urls', namespace='words',)),
    path('games/', include('memorisation.urls')),

    path('', index,  name='home'),
    path('api/users/<str:username>/cards/', cards, name='cards'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
