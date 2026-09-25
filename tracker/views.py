from django.shortcuts import render, get_object_or_404, redirect
from .models import KBBoard, UserBoard, KBColumn, Task
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User


# Create your views here.
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
            login(request, user)
            return redirect("board_list")
        else:
            return render(
                request,
                "tracker/login.html",
                {"error": "Invalid username or password.", "show_signup_link": True},
            )
    return render(request, "tracker/login.html")


def board_list(request):
    boards = KBBoard.objects.all()
    return render(request, "tracker/board_list.html", {"boards": boards})


def board_detail(request, board_id):
    board = get_object_or_404(KBBoard, id=board_id)

    # Дістаємо всі колонки, які належать саме цій дошці
    columns = KBColumn.objects.filter(board=board)

    # Обов'язково передаємо словник з 'columns' у шаблон!
    return render(
        request, "tracker/board_detail.html", {"board": board, "columns": columns}
    )


def logout_view(request):
    logout(request)
    return redirect("index")


def create_board(request):
    # Якщо користувач не увійшов, відправляємо на логін
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        b_name = request.POST.get("board_name")

        new_board = KBBoard.objects.create(name=b_name)
        UserBoard.objects.create(user=request.user, board=new_board, role="owner")

        return redirect("board_detail", board_id=new_board.id)

    # Якщо це GET-запит (користувач просто натиснув на плюсик)
    return render(request, "tracker/create_board.html")


def add_column(request, board_id):
    if request.method == "POST" and request.user.is_authenticated:
        board = get_object_or_404(KBBoard, id=board_id)
        col_name = request.POST.get("column_name")

        # Автоматично вираховуємо позицію (остання + 1)
        next_position = board.columns.count() + 1

        KBColumn.objects.create(board=board, name=col_name, position=next_position)

    return redirect("board_detail", board_id=board_id)


def add_task(request, column_id):
    if request.method == "POST" and request.user.is_authenticated:
        column = get_object_or_404(KBColumn, id=column_id)
        task_name = request.POST.get("task_name")

        # Автоматично вираховуємо позицію задачі в колонці
        next_position = column.tasks.count() + 1

        Task.objects.create(column=column, name=task_name, position=next_position)

        # Щоб зробити редірект на дошку, дістаємо її ID через зв'язок з колонкою
        return redirect("board_detail", board_id=column.board.id)

    # Резервний редірект, якщо щось пішло не так
    return redirect("board_list")
