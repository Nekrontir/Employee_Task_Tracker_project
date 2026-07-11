from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # менеджер, под которым будем делать CRUD
        self.manager = User.objects.create_user(
            email="manager@example.com",
            full_name="Manager",
            password="managerpass",
            role="manager",
        )
        self.client.force_authenticate(user=self.manager)

        # существующий сотрудник
        self.employee = User.objects.create_user(
            email="employee@example.com",
            full_name="Employee",
            password="password",
            role="employee",
            position="Developer",
        )

        self.list_url = reverse("user-list")
        self.detail_url = reverse("user-detail", args=[self.employee.id])

    def test_user_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # поддерживаем пагинацию: берём results
        if isinstance(data, dict) and "results" in data:
            users = data["results"]
        else:
            users = data

        emails = [u.get("email") for u in users if isinstance(u, dict)]
        self.assertIn("manager@example.com", emails)
        self.assertIn("employee@example.com", emails)

    def test_user_create(self):
        payload = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "position": "Tester",
            "role": "employee",
            "password": "newpass123",
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_user_update(self):
        payload = {
            "email": "employee@example.com",
            "full_name": "Employee Updated",
            "position": "Senior Developer",
            "role": "employee",
            "password": "password",
        }
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.full_name, "Employee Updated")
        self.assertEqual(self.employee.position, "Senior Developer")

    def test_user_delete(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.employee.id).exists())
        
        
class JWTAuthTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="jwtuser@example.com",
            full_name="JWT User",
            password="jwtpass123",
            role="employee",
        )
        self.token_url = reverse("token_obtain_pair")

    def test_obtain_jwt_token(self):
        payload = {
            "email": "jwtuser@example.com",
            "password": "jwtpass123",
        }
        response = self.client.post(self.token_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_access_protected_endpoint_with_jwt(self):
        # получаем токен
        payload = {
            "email": "jwtuser@example.com",
            "password": "jwtpass123",
        }
        response = self.client.post(self.token_url, payload, format="json")
        access = response.json()["access"]

        # используем его для доступа к защищённому эндпоинту (например, /api/tasks/)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        tasks_url = reverse("task-list")
        response2 = self.client.get(tasks_url)
        self.assertNotEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)