from django.shortcuts import render, get_object_or_404, redirect
from .models import KBBoard, UserBoard, KBColumn, Task, BoardInvitation
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from .models import UserProfile
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max


def index(request):
    return render(request, "tracker/index.html")


def signup_view(request):
    if request.method == "POST":
        user_name = request.POST.get("username")
        email_address = request.POST.get("email")
        pass_word = request.POST.get("password")

        if User.objects.filter(username=user_name).exists():
            return render(
                request,
                "tracker/signup.html",
                {"error": "This username is already taken. Please choose another one."},
            )

        user = User.objects.create_user(
            username=user_name, email=email_address, password=pass_word
        )
        login(request, user)
        return redirect("board_list")
    return render(request, "tracker/signup.html")


def login_view(request):
    if request.method == "POST":
        user_name = request.POST.get("username")
        pass_word = request.POST.get("password")

        user = authenticate(request, username=user_name, password=pass_word)

        if user is not None:
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect("board_list")
        else:
            return render(
                request,
                "tracker/login.html",
                {"error": "Invalid username or password.", "show_signup_link": True},
            )
    return render(request, "tracker/login.html")


@login_required
def board_list(request):
    allowed_board_ids = UserBoard.objects.filter(user=request.user).values_list(
        "board_id", flat=True
    )

    boards = KBBoard.objects.filter(id__in=allowed_board_ids)

    invitations = BoardInvitation.objects.filter(receiver=request.user)

    return render(
        request,
        "tracker/board_list.html",
        {"boards": boards, "invitations": invitations},
    )


@login_required
def board_detail(request, board_id):
    board = get_object_or_404(KBBoard, id=board_id)

    try:
        current_link = UserBoard.objects.get(user=request.user, board=board)
        role = current_link.role
    except UserBoard.DoesNotExist:
        return redirect("board_list")

    columns = KBColumn.objects.filter(board=board)
    participants = UserBoard.objects.filter(board=board)
    pending_invites = BoardInvitation.objects.filter(board=board)

    return render(
        request,
        "tracker/board_detail.html",
        {
            "board": board,
            "columns": columns,
            "participants": participants,
            "pending_invites": pending_invites,
            "is_owner": (role == "owner"),
            "can_edit": (role in ["owner", "editor"]),
        },
    )


@login_required
def invite_user(request, board_id):
    if request.method == "POST":
        username = request.POST.get("username")
        role = request.POST.get("role", "editor")
        board = get_object_or_404(KBBoard, id=board_id)

        try:
            receiver = User.objects.get(username=username)
            in_board = UserBoard.objects.filter(user=receiver, board=board).exists()
            already_invited = BoardInvitation.objects.filter(
                receiver=receiver, board=board
            ).exists()

            if not in_board and not already_invited and receiver != request.user:
                BoardInvitation.objects.create(
                    board=board, sender=request.user, receiver=receiver, role=role
                )
        except User.DoesNotExist:
            pass
    return redirect("board_detail", board_id=board_id)


@login_required
def cancel_invite(request, invite_id):
    if request.method == "POST":
        invite = get_object_or_404(BoardInvitation, id=invite_id)
        board_id = invite.board.id
        invite.delete()
        return redirect("board_detail", board_id=board_id)
    return redirect("board_list")


@login_required
def respond_invite(request, invite_id, action):
    invite = get_object_or_404(BoardInvitation, id=invite_id, receiver=request.user)
    if action == "accept":
        UserBoard.objects.create(
            user=request.user, board=invite.board, role=invite.role
        )
    invite.delete()
    return redirect("board_list")


@login_required
def update_user_role(request, board_id, link_id):
    if request.method == "POST":
        new_role = request.POST.get("new_role")
        target_link = get_object_or_404(UserBoard, id=link_id, board_id=board_id)

        if new_role == "owner":
            current_owner_link = UserBoard.objects.get(
                user=request.user, board_id=board_id
            )
            current_owner_link.role = "editor"
            current_owner_link.save()
            target_link.role = "owner"
            target_link.save()
        else:
            target_link.role = new_role
            target_link.save()

    return redirect("board_detail", board_id=board_id)


def logout_view(request):
    logout(request)
    return redirect("index")


def create_board(request):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        b_name = request.POST.get("board_name")

        new_board = KBBoard.objects.create(name=b_name)
        UserBoard.objects.create(user=request.user, board=new_board, role="owner")

        return redirect("board_detail", board_id=new_board.id)

    return render(request, "tracker/create_board.html")


def add_column(request, board_id):
    if request.method == "POST" and request.user.is_authenticated:
        board = get_object_or_404(KBBoard, id=board_id)
        col_name = request.POST.get("column_name")

        next_position = board.columns.count() + 1

        KBColumn.objects.create(board=board, name=col_name, position=next_position)

    return redirect("board_detail", board_id=board_id)


@login_required
def add_task(request, column_id):
    column = get_object_or_404(KBColumn, id=column_id)
    user_board = get_object_or_404(UserBoard, user=request.user, board=column.board)

    if user_board.role in ["owner", "editor"] and request.method == "POST":
        task_name = request.POST.get("task_name")
        if task_name:
            max_pos = column.tasks.aggregate(Max("position"))["position__max"]
            next_pos = (max_pos + 1) if max_pos is not None else 0

            Task.objects.create(column=column, name=task_name, position=next_pos)

    return redirect("board_detail", board_id=column.board.id)


def delete_column(request, column_id):
    if request.method == "POST" and request.user.is_authenticated:
        column = get_object_or_404(KBColumn, id=column_id)
        board_id = column.board.id
        column.delete()
        return redirect("board_detail", board_id=board_id)
    return redirect("board_list")


def delete_task(request, task_id):
    if request.method == "POST" and request.user.is_authenticated:
        task = get_object_or_404(Task, id=task_id)
        board_id = task.column.board.id
        task.delete()
        return redirect("board_detail", board_id=board_id)
    return redirect("board_list")


@login_required
def toggle_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user_board = get_object_or_404(
        UserBoard, user=request.user, board=task.column.board
    )

    if user_board.role in ["owner", "editor"] and request.method == "POST":
        task.status = not task.status
        task.save(update_fields=["status"])

    return redirect("board_detail", board_id=task.column.board.id)


def rename_item(request, item_type, item_id):
    if request.method == "POST" and request.user.is_authenticated:
        new_name = request.POST.get("new_name")
        if not new_name:
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if item_type == "board":
            obj = get_object_or_404(KBBoard, id=item_id)
            obj.name = new_name
            obj.save()
            return redirect("board_detail", board_id=obj.id)

        elif item_type == "column":
            obj = get_object_or_404(KBColumn, id=item_id)
            obj.name = new_name
            obj.save()
            return redirect("board_detail", board_id=obj.board.id)

        elif item_type == "task":
            obj = get_object_or_404(Task, id=item_id)
            obj.name = new_name
            obj.save()
            return redirect("board_detail", board_id=obj.column.board.id)

    return redirect("board_list")


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user_board = get_object_or_404(
        UserBoard, user=request.user, board=task.column.board
    )

    if user_board.role not in ["owner", "editor"]:
        return redirect("board_detail", board_id=task.column.board.id)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        start_date = request.POST.get("start_date")
        deadline = request.POST.get("deadline")

        if start_date and deadline and start_date > deadline:
            return render(
                request,
                "tracker/task_edit.html",
                {"task": task, "error": "Start date cannot be later than deadline!"},
            )

        task.name = name
        task.description = description

        task.start_date = start_date if start_date else None
        task.deadline = deadline if deadline else None

        task.save()
        return redirect("board_detail", board_id=task.column.board.id)

    return render(request, "tracker/task_edit.html", {"task": task})


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    UserProfile.objects.get_or_create(user=profile_user)
    return render(request, "tracker/profile.html", {"profile_user": profile_user})


@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        bio = request.POST.get("bio")
        avatar = request.FILES.get("avatar")

        profile.bio = bio
        if avatar:
            profile.avatar = avatar
        profile.save()

        return redirect("profile", username=request.user.username)

    return render(request, "tracker/profile_edit.html", {"profile": profile})


@login_required
@csrf_exempt
def reorder_items(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_type = data.get("type")

        if item_type == "column":
            for index, col_id in enumerate(data.get("order", [])):
                KBColumn.objects.filter(id=col_id).update(position=index)
            return JsonResponse({"status": "ok"})

        elif item_type == "task":
            task_id = data.get("task_id")
            target_col_id = data.get("target_column_id")
            new_position = data.get("new_position")

            task = get_object_or_404(Task, id=task_id)
            if target_col_id:
                task.column_id = target_col_id
            task.position = new_position
            task.save()
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "bad request"}, status=400)


@login_required
def delete_board(request, board_id):
    board = get_object_or_404(KBBoard, id=board_id)
    user_board = get_object_or_404(UserBoard, user=request.user, board=board)

    if user_board.role == "owner" and request.method == "POST":
        board.delete()
        return redirect("board_list")

    return redirect("board_detail", board_id=board.id)
