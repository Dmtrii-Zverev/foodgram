from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    '''Изменение и удаление объекта.
    Разрешает создателю объекта модель и  администратору
    изменять/удалять объект. Остальным только читать.
    '''
    def has_permission(self, request, view):
        if view.action == 'download_api_text':
            return request.user.is_authenticated
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif view.action == 'shopping_cart' or view.action == 'favorite_cart':
            return request.user.is_authenticated
        return (
            obj.author == request.user
            or request.user.is_staff
        )
    

class IsAdminOrAuthUserOrReadonly(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        elif view.action == 'subscriptions':
            return request.user.is_authenticated
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if view.action == 'subscribe':
            return request.user.is_authenticated
        elif request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_staff
            or obj == request.user
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает полный доступ администраторам, остальным только чтение."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif not request.user.is_staff:
            raise MethodNotAllowed(request.method)
        return request.user.is_staff
