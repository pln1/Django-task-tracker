from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("boards/", views.board_list, name="board_list"),
    path("boards/<int:board_id>/", views.board_detail, name="board_detail"),
    path("logout/", views.logout_view, name="logout"),
    path("boards/create/", views.create_board, name="create_board"),
    path("boards/<int:board_id>/add_column/", views.add_column, name="add_column"),
    path("columns/<int:column_id>/add_task/", views.add_task, name="add_task"),
]
