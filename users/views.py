from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer, UserCreateSerializer


class IsManager(permissions.BasePermission):
    """
    Разрешает доступ только пользователям с ролью менеджера.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "manager"
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD для сотрудников/пользователей.

    - Менеджер видит и управляет всеми пользователями.
    - Обычный сотрудник по умолчанию видит и изменяет только себя.
    """

    queryset = User.objects.all().order_by("full_name")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        # Для простоты: менеджер имеет полный доступ ко всем операциям.
        if self.action in ("list", "retrieve", "create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsManager()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "manager":
            return User.objects.all().order_by("full_name")
        # сотрудник видит только себя
        return User.objects.filter(id=user.id)