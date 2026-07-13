from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import User

from .models import Task


class TaskViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # менеджер
        self.manager = User.objects.create_user(
            email="manager_tasks@example.com",
            full_name="Manager Tasks",
            password="managerpass",
            role="manager",
        )
        self.client.force_authenticate(user=self.manager)

        # сотрудник-исполнитель
        self.employee = User.objects.create_user(
            email="task_emp@example.com",
            full_name="Task Employee",
            password="password",
            role="employee",
        )

        # существующая задача
        self.task = Task.objects.create(
            title="Existing Task",
            description="Test task",
            assignee=self.employee,
            status=Task.Status.NEW,
            priority=Task.Priority.MEDIUM,
        )

        self.list_url = reverse("task-list")
        self.detail_url = reverse("task-detail", args=[self.task.id])

    def test_task_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # поддерживаем пагинацию
        if isinstance(data, dict) and "results" in data:
            tasks = data["results"]
        else:
            tasks = data

        titles = [t.get("title") for t in tasks if isinstance(t, dict)]
        self.assertIn("Existing Task", titles)

    def test_task_create(self):
        payload = {
            "title": "New Task",
            "description": "New task description",
            "assignee_id": self.employee.id,
            "status": Task.Status.NEW,
            "priority": Task.Priority.HIGH,
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Task.objects.filter(title="New Task").exists())

    def test_task_update(self):
        payload = {
            "title": "Updated Task",
            "description": "Updated description",
            "assignee_id": self.employee.id,
            "status": Task.Status.IN_PROGRESS,
            "priority": Task.Priority.CRITICAL,
        }
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")
        self.assertEqual(self.task.status, Task.Status.IN_PROGRESS)
        self.assertEqual(self.task.priority, Task.Priority.CRITICAL)

    def test_task_delete(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
