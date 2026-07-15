from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_view, name="ui-dashboard"),
    path("users/", views.users_list_view, name="ui-users"),
    path("tasks/", views.tasks_list_view, name="ui-tasks"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="ui-task-create"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="ui-task-detail"),
    path("tasks/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="ui-task-edit"),
    path("tasks/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="ui-task-delete"),
    path("analytics/", views.analytics_view, name="ui-analytics"),
    path(
        "login/",
        LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True,
        ),
        name="ui-login",
    ),
    path("logout/", views.logout_view, name="ui-logout"),
]
