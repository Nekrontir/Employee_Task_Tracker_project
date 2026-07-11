from django.db import models
from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD для задач сотрудников.

    - Менеджер видит все задачи.
    - Сотрудник видит задачи, где он исполнитель или создатель.
    """

    queryset = Task.objects.select_related("assignee", "created_by", "parent_task").all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "manager":
            return Task.objects.select_related("assignee", "created_by", "parent_task").all()
        return (
            Task.objects.select_related("assignee", "created_by", "parent_task")
            .filter(
                models.Q(assignee=user) | models.Q(created_by=user),
            )
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)