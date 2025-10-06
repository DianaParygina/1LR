from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользовательское разрешение, позволяющее редактировать (PUT, DELETE) объект
    только его владельцу. Разрешает чтение (GET) всем аутентифицированным пользователям.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить GET, HEAD или OPTIONS запросы (READ) всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить операции WRITE (PUT, DELETE) только владельцу объекта.
        # Предполагается, что объект (Dog, Owner) имеет атрибут 'user'.
        return obj.user == request.user
