from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.ProfileTemplateView.as_view(), name="profile"),
    path(
        "profile/update/",
        views.ProfileUpdateView.as_view(),
        name="profile_update",
    ),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("signup/", views.UserSignUpView.as_view(), name="signup"),
    path("room/", views.RoomTemplateView.as_view(), name="room"),
    # path("room_join/", views.RoomJoinView.as_view(), name="room_join"),
    path(
        "room_join_invitation/",
        views.RoomInvitationJoinView.as_view(),
        name="room_invitation_join",
    ),
    path("room_create/", views.RoomCreateView.as_view(), name="room_create"),
    path("room_selection/", views.RoomSelectionView.as_view(), name="room_selection"),
    path(
        "room_invitation/",
        views.RoomInvitationListView.as_view(),
        name="room_invitation",
    ),
    path(
        "room_invite/",
        views.RoomInviteView.as_view(),
        name="room_invite",
    ),
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.MyPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
