from rest_framework import permissions


class IsAdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(IsAdminOnly):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or super().has_permission(request, view))


class IsAuthorOrStuffOrReadOnly(permissions.BasePermission):
    message = 'Изменение чужого контента запрещено!'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator)
