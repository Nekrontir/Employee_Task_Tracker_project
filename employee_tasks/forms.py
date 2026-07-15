from django import forms

from users.models import User

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "assignee",
            "deadline",
            "status",
            "priority",
            "parent_task",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is None:
            self.fields["assignee"].queryset = User.objects.none()
            self.fields["parent_task"].queryset = Task.objects.all().order_by("title")
            return

        is_manager_or_admin = user.is_staff or user.role == "manager"

        if is_manager_or_admin:
            self.fields["assignee"].queryset = User.objects.all().order_by("full_name")
        else:
            self.fields["assignee"].queryset = User.objects.filter(pk=user.pk)

        self.fields["parent_task"].queryset = Task.objects.all().order_by("title")
