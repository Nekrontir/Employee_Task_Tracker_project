from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Count, Min, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from employee_tasks.forms import TaskForm
from employee_tasks.models import Task
from users.models import User


def dashboard_view(request):
    context = {"title": "Панель управления"}
    return render(request, "dashboard.html", context)


def users_list_view(request):
    users = User.objects.all().order_by("last_name", "first_name")
    context = {
        "title": "Сотрудники",
        "users": users,
    }
    return render(request, "users_list.html", context)


def tasks_list_view(request):
    priority = request.GET.get("priority")
    tasks_qs = Task.objects.select_related("assignee", "parent_task")

    if priority in [Task.Priority.LOW, Task.Priority.MEDIUM, Task.Priority.HIGH, Task.Priority.CRITICAL]:
        tasks_qs = tasks_qs.filter(priority=priority)

    tasks = tasks_qs.all()

    context = {
        "title": "Задачи",
        "tasks": tasks,
        "selected_priority": priority,
    }
    return render(request, "tasks_list.html", context)


class TaskDetailView(DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("ui-tasks")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        is_manager_or_admin = self.request.user.is_staff or self.request.user.role == "manager"

        form.instance.created_by = self.request.user
        if not is_manager_or_admin:
            form.instance.assignee = self.request.user

        messages.success(self.request, "Задача создана.")
        return super().form_valid(form)


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("ui-tasks")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        is_manager_or_admin = self.request.user.is_staff or self.request.user.role == "manager"

        if not is_manager_or_admin:
            form.instance.assignee = self.request.user

        messages.success(self.request, "Задача обновлена.")
        return super().form_valid(form)

class TaskDeleteView(DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("ui-tasks")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Задача удалена.")
        return super().delete(request, *args, **kwargs)



def analytics_view(request):
    # Активные статусы задач
    active_statuses = [
        Task.Status.NEW,
        Task.Status.IN_PROGRESS,
        Task.Status.BLOCKED,
    ]

    # 1. Занятые сотрудники: считаем количество активных задач на каждого
    busy_employees = User.objects.annotate(
        active_tasks_count=Count(
            "assigned_tasks",
            filter=Q(assigned_tasks__status__in=active_statuses),
        )
    ).order_by("-active_tasks_count", "last_name", "first_name")

    # Минимальная загруженность (для поиска наименее загруженных)
    min_load = (
        busy_employees.aggregate(min_count=Min("active_tasks_count"))["min_count"] if busy_employees.exists() else 0
    )

    # 2. Важные задачи:
    # задачи без исполнителя, от которых зависят задачи в работе
    important_tasks_qs = Task.objects.filter(
        assignee__isnull=True,
        child_tasks__status__in=active_statuses,
    ).distinct()

    important_tasks = []

    for task in important_tasks_qs:
        # Наименее загруженные сотрудники
        least_loaded = busy_employees.filter(active_tasks_count=min_load)

        # Сотрудник, выполняющий родительскую задачу
        parent_assignees = User.objects.none()
        if task.parent_task and task.parent_task.assignee:
            parent_assignee = busy_employees.filter(pk=task.parent_task.assignee.pk).first()
            if parent_assignee and parent_assignee.active_tasks_count <= min_load + 2:
                parent_assignees = User.objects.filter(pk=parent_assignee.pk)

        # Объединяем списки сотрудников
        suggested_employees = (least_loaded | parent_assignees).distinct()

        important_tasks.append(
            {
                "task": task,
                "deadline": task.deadline,
                "suggested_employees": suggested_employees,
            }
        )

    context = {
        "title": "Аналитика",
        "busy_employees": busy_employees,
        "important_tasks": important_tasks,
    }
    return render(request, "analytics.html", context)


def logout_view(request):
    logout(request)
    return redirect("ui-dashboard")
