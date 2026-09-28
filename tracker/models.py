from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    start_date = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name

    @property
    def is_overdue(self):
        if self.deadline and not self.status:
            return self.deadline < timezone.now()
        return False

    @property
    def is_planned(self):
        if self.start and not self.status:
            return self.start > timezone.now()
        return False


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)


class BoardInvitation(models.Model):
    board = models.ForeignKey(
        KBBoard, on_delete=models.CASCADE, related_name="invitations"
    )
    inviter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_invites"
    )
    invitee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_invites"
    )
    role = models.CharField(
        max_length=20, choices=[("viewer", "Viewer"), ("editor", "Editor")]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite for {self.invitee.username} to {self.board.name}"
