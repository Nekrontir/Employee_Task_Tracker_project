from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import User

from .models import Task


class BusyEmployeesTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # создаём менеджера и логинимся под ним (JWT/Session не важны, в тестах клиент автоматически аутентифицирован)
        self.manager = User.objects.create_user(
            email="manager@example.com",
            full_name="Manager",
            password="managerpass",
            role="manager",
        )
        self.client.force_authenticate(user=self.manager)

        # создаём сотрудников
        self.employee1 = User.objects.create_user(
            email="emp1@example.com",
            full_name="Employee One",
            password="password",
            role="employee",
            position="Backend Developer",
        )
        self.employee2 = User.objects.create_user(
            email="emp2@example.com",
            full_name="Employee Two",
            password="password",
            role="employee",
            position="QA Engineer",
        )

        # создаём задачи: у employee1 две активные, у employee2 одна
        Task.objects.create(
            title="Task 1",
            assignee=self.employee1,
            status=Task.Status.IN_PROGRESS,
        )
        Task.objects.create(
            title="Task 2",
            assignee=self.employee1,
            status=Task.Status.NEW,
        )
        Task.objects.create(
            title="Task 3",
            assignee=self.employee2,
            status=Task.Status.BLOCKED,
        )

        # неактивная задача (DONE) не должна учитываться
        Task.objects.create(
            title="Task 4",
            assignee=self.employee2,
            status=Task.Status.DONE,
        )

    def test_busy_employees_returns_sorted_list(self):
        url = reverse("busy-employees")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # ожидаем двух сотрудников в ответе
        self.assertEqual(len(data), 2)

        # первый — наиболее загруженный (employee1 с 2 задачами)
        self.assertEqual(data[0]["full_name"], "Employee One")
        self.assertEqual(data[0]["active_tasks_count"], 2)

        # второй — employee2 с 1 активной задачей
        self.assertEqual(data[1]["full_name"], "Employee Two")
        self.assertEqual(data[1]["active_tasks_count"], 1)


class ImportantTasksTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.manager = User.objects.create_user(
            email="manager2@example.com",
            full_name="Manager Two",
            password="managerpass",
            role="manager",
        )
        self.client.force_authenticate(user=self.manager)

        # сотрудники
        self.least_loaded = User.objects.create_user(
            email="least@example.com",
            full_name="Least Loaded",
            password="password",
            role="employee",
        )
        self.busy_employee = User.objects.create_user(
            email="busy@example.com",
            full_name="Busy Employee",
            password="password",
            role="employee",
        )

        # считаем активные задачи:
        # least_loaded — 1 задача
        Task.objects.create(
            title="LL Task 1",
            assignee=self.least_loaded,
            status=Task.Status.IN_PROGRESS,
        )

        # busy_employee — 3 активные (на 2 больше, чем у least_loaded)
        Task.objects.create(
            title="BE Task 1",
            assignee=self.busy_employee,
            status=Task.Status.NEW,
        )
        Task.objects.create(
            title="BE Task 2",
            assignee=self.busy_employee,
            status=Task.Status.IN_PROGRESS,
        )
        Task.objects.create(
            title="BE Task 3",
            assignee=self.busy_employee,
            status=Task.Status.BLOCKED,
        )

        # важная задача: не взята в работу (NEW, assignee=None)
        self.important_task = Task.objects.create(
            title="Important Task",
            status=Task.Status.NEW,
            assignee=None,
        )

        # дочерняя задача в работе, исполнитель — busy_employee
        Task.objects.create(
            title="Child Task in Work",
            parent_task=self.important_task,
            assignee=self.busy_employee,
            status=Task.Status.IN_PROGRESS,
        )

    def test_important_tasks_returns_task_and_suggested_employees(self):
        url = reverse("important-tasks")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # ожидаем одну важную задачу
        self.assertEqual(len(data), 1)
        item = data[0]

        self.assertEqual(item["important_task"], "Important Task")

        # сотрудники: Least Loaded (наименее загруженный) и Busy Employee (исполнитель дочерней задачи,
        # у него нагрузки ровно min_load + 2, что подходит под условие)
        employees = item["employees"]
        self.assertIn("Least Loaded", employees)
        self.assertIn("Busy Employee", employees)
