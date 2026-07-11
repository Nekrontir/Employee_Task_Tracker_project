from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "assignee",
        "status",
        "priority",
        "deadline",
        "parent_task",
        "created_at",
    )
    list_filter = ("status", "priority", "deadline")
    search_fields = ("title", "description", "assignee__full_name", "assignee__email")
    date_hierarchy = "deadline"
    autocomplete_fields = ("assignee", "created_by", "parent_task")
