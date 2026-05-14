from django.contrib import admin

from .models import ExternalIdentity, Role, User, UserRole


admin.site.register(User)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(ExternalIdentity)
