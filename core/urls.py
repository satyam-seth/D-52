from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.AboutTemplateView.as_view(), name="about"),
    path("feedback/", views.FeedbackCreateView.as_view(), name="feedback"),
]
