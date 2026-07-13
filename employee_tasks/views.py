from django.db import models
from django.db.models import Count, Min, Q
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .models import Task
from .serializers import BusyEmployeeSerializer, ImportantTaskSerializer, TaskSerializer


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
        return Task.objects.select_related("assignee", "created_by", "parent_task").filter(
            models.Q(assignee=user) | models.Q(created_by=user),
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BusyEmployeesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=BusyEmployeeSerializer(many=True),
        description="Список сотрудников и количество их активных задач.",
    )
    def get(self, request):
        active_statuses = [
            Task.Status.NEW,
            Task.Status.IN_PROGRESS,
            Task.Status.BLOCKED,
        ]

        qs = (
            User.objects.filter(role="employee", is_active_employee=True)
            .annotate(
                active_tasks_count=Count(
                    "assigned_tasks",
                    filter=Q(assigned_tasks__status__in=active_statuses),
                )
            )
            .order_by("-active_tasks_count", "full_name")
        )

        data = [
            {
                "id": user.id,
                "full_name": user.full_name,
                "position": user.position or "",
                "active_tasks_count": user.active_tasks_count,
            }
            for user in qs
        ]

        serializer = BusyEmployeeSerializer(data, many=True)
        return Response(serializer.data)


class ImportantTasksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=ImportantTaskSerializer(many=True),
        description="Список важных задач и рекомендуемых сотрудников.",
    )
    def get(self, request):
        active_statuses = [
            Task.Status.NEW,
            Task.Status.IN_PROGRESS,
            Task.Status.BLOCKED,
        ]
        in_work_statuses = [
            Task.Status.IN_PROGRESS,
            Task.Status.BLOCKED,
        ]

        # загрузка сотрудников
        employees_qs = User.objects.filter(role="employee", is_active_employee=True).annotate(
            active_tasks_count=Count(
                "assigned_tasks",
                filter=Q(assigned_tasks__status__in=active_statuses),
            )
        )

        if not employees_qs.exists():
            serializer = ImportantTaskSerializer([], many=True)
            return Response(serializer.data)

        min_load = employees_qs.aggregate(min_load=Min("active_tasks_count"))["min_load"]

        # важные задачи
        important_tasks_qs = (
            Task.objects.filter(
                status=Task.Status.NEW,
                assignee__isnull=True,
            )
            .filter(
                child_tasks__status__in=in_work_statuses,
                child_tasks__assignee__isnull=False,
            )
            .distinct()
        )

        results = []

        for task in important_tasks_qs:
            # наименее загруженные
            least_loaded = employees_qs.filter(active_tasks_count=min_load)

            # исполнители дочерних задач в работе
            child_assignees = User.objects.filter(
                assigned_tasks__parent_task=task,
                assigned_tasks__status__in=in_work_statuses,
            ).distinct()

            suggested_employees = set()

            for emp in least_loaded:
                suggested_employees.add(emp.full_name)

            for emp in child_assignees:
                suggested_employees.add(emp.full_name)

            results.append(
                {
                    "important_task": task.title,
                    "deadline": task.deadline,
                    "employees": sorted(suggested_employees),
                }
            )

        serializer = ImportantTaskSerializer(results, many=True)
        return Response(serializer.data)
