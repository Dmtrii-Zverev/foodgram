# users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Photo', {'fields': ('avatar',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('email', 'first_name', 'last_name'),
        }),
    )
    search_fields = UserAdmin.search_fields + ('email', 'username')
