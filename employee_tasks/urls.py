from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BusyEmployeesView, ImportantTasksView, TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
    path("busy-employees/", BusyEmployeesView.as_view(), name="busy-employees"),
    path("important-tasks/", ImportantTasksView.as_view(), name="important-tasks"),
]
