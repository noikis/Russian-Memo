from django.contrib import admin

from .models import Card, Deck

# Register your models here.
admin.site.register(Card)


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("category", "color", "student", "created_at", "deleted_at")
