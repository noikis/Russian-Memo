from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import index
from words.views import cards, fetch_cards

app_name = 'main'
name_space = 'main'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls', namespace='account',)),
    path('quiz/', include('quiz.urls', namespace='quiz',)),
    path('words/', include('words.urls', namespace='words',)),
    path('games/', include('memorisation.urls')),

    path('', index,  name='home'),
    path('api/cards/', cards, name='cards'),
    path('fetch/', fetch_cards, name='fetch_cards'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
