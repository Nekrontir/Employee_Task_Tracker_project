from django.urls import path

from . import views

urlpatterns = [
    path("/", views.dashboard_view, name="ui-dashboard"),
    path("users/", views.users_list_view, name="ui-users"),
    path("tasks/", views.tasks_list_view, name="ui-tasks"),
    path("analytics/", views.analytics_view, name="ui-analytics"),
]
