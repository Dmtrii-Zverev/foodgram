# api_v1/permissions.py

from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """Изменение и удаление объекта.
    Разрешает создателю объекта модель и  администратору
    изменять/удалять объект. Остальным только читать.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.is_admin
            or obj == request.user
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает полный доступ администраторам, остальным только чтение."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin
