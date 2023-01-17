from core import views
from django.contrib.auth import views as auth_views
from django.urls import path

# TODO: add namespace  'app = "core"'

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.AboutTemplateView.as_view(), name="about"),
    path("feedback/", views.FeedbackCreateView.as_view(), name="feedback"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogout.as_view(), name="logout"),
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
