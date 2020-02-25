from django.contrib.admin import ModelAdmin, register

from .models import Practice


@register(Practice)
class PracticeAdmin(ModelAdmin):
    list_display = ('card', 'easy_factor',
                    'next_practice', 'times_practiced', )

    order_by = ['student']
