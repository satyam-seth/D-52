from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import FeedbackFrom

# Create your views here.


class HomeTemplateView(TemplateView):
    """View to server home page template"""

    template_name = "core/home.html"
    extra_context = {"home_active": "active"}


# TODO: Update wording and doc for view template
class AboutTemplateView(TemplateView):
    """View to render the about page template."""

    template_name = "core/about.html"
    extra_context = {"about_active": "active"}


class FeedbackCreateView(SuccessMessageMixin, CreateView):
    """View  to handle the creation of user feedback"""

    form_class = FeedbackFrom
    success_url = reverse_lazy("core:home")
    template_name = "core/feedback.html"
    success_message = (
        "Thank you for your valuable feedback, "
        + "it will help us to improve your experience."
    )
    extra_context = {"feedback_active": "active"}
