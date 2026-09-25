from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class KBBoard(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    def get_effective_role(self, user):
        if not self.status:
            return "viewer"

        try:
            user_access = self.users.get(user=user)
            return user_access.role
        except UserBoard.DoesNotExist:
            return None

    def __str__(self):
        return self.name


class UserBoard(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("editor", "Editor"),
        ("viewer", "Viewer"),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="board_accesses"
    )
    board = models.ForeignKey(KBBoard, on_delete=models.CASCADE, related_name="users")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="viewer")

    class Meta:
        unique_together = ("user", "board")

    def __str__(self):
        return f"{self.user.username} - {self.board.name} ({self.role})"


class KBColumn(models.Model):
    board = models.ForeignKey(KBBoard, on_delete=models.CASCADE, related_name="columns")
    name = models.CharField(max_length=255)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.board.name} | {self.name}"


class Task(models.Model):
    column = models.ForeignKey(KBColumn, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name
