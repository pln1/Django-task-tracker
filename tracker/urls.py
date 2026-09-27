from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings  # ДОДАТИ
from django.conf.urls.static import static  # ДОДАТИ

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
    path("columns/<int:column_id>/delete/", views.delete_column, name="delete_column"),
    path("tasks/<int:task_id>/delete/", views.delete_task, name="delete_task"),
    path(
        "tasks/<int:task_id>/toggle/",
        views.toggle_task_status,
        name="toggle_task_status",
    ),
    path("tasks/<int:task_id>/edit/", views.edit_task, name="edit_task"),
    path(
        "rename/<str:item_type>/<int:item_id>/", views.rename_item, name="rename_item"
    ),
    path(
        "boards/<int:board_id>/update_role/<int:link_id>/",
        views.update_user_role,
        name="update_user_role",
    ),
    path("boards/<int:board_id>/invite/", views.invite_user, name="invite_user"),
    path("invites/<int:invite_id>/cancel/", views.cancel_invite, name="cancel_invite"),
    path(
        "invites/<int:invite_id>/respond/<str:action>/",
        views.respond_invite,
        name="respond_invite",
    ),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path("profile-edit/", views.profile_edit, name="profile_edit"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="tracker/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="tracker/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="tracker/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="tracker/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("api/reorder/", views.reorder_items, name="reorder_items"),
    path("boards/<int:board_id>/delete/", views.delete_board, name="delete_board"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
