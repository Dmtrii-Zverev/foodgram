# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

UserAdmin.fieldsets += (
    ('Photo', {'fields': ('avatar',)}),
)
admin.site.register(CustomUser, UserAdmin)
