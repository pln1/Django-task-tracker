from django.contrib import admin
from .models import KBBoard, UserBoard, KBColumn, Task, UserProfile, BoardInvitation

# Register your models here.
admin.site.register(KBBoard)
admin.site.register(UserBoard)
admin.site.register(KBColumn)
admin.site.register(Task)
admin.site.register(UserProfile)
admin.site.register(BoardInvitation)
