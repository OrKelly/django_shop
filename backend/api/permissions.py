from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Проверяем, стафф ли авторизованный пользователь. Если нет - включается режим только для чтения"""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff
