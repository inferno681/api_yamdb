from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS
                    or request.user.is_authenticated
                    and request.user.is_admin)


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(obj.author == request.user
                    or request.user.is_admin
                    or request.user.role == 'moderator')


class IsAdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or request.user.is_superuser


class IsAuthorOrStuffOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        self.message = 'Изменение чужого контента запрещено!'
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator)
