from rest_framework import serializers
from .models import Task
from users.serializers import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=Task._meta.get_field("assignee").remote_field.model.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=Task._meta.get_field("created_by").remote_field.model.objects.all(),
        source="created_by",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "assignee",
            "assignee_id",
            "created_by",
            "created_by_id",
            "deadline",
            "status",
            "priority",
            "parent_task",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")