from typing import Any, Dict

from data.models import Record, Water
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordResetCompleteView)
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, TemplateView

from .forms import FeedbackFrom, LoginForm
from .models import Electricity, Maid

User = get_user_model()

# TODO: fix this view
# TODO: Add login required once user group login achieved make another page for signup - intro
def home(request):
    # TODO: handle empty database state
    w_sum = Water.objects.aggregate(Sum("quantity"))["quantity__sum"]
    w_price = 40 * w_sum
    w_pp = w_price / 4

    # TODO: handle empty database state
    electricity = Electricity.objects.latest("due_date")
    e_pp = electricity.price / 4
    e_days_left = (electricity.due_date - timezone.now().date()).days

    # TODO: handle empty database state
    maid = Maid.objects.latest("due_date")
    m_pp = maid.price / 4
    m_days_left = (maid.due_date - timezone.now().date()).days

    # TODO: remove hardcoded group name
    users = User.objects.filter(groups__name="d52")

    # TODO: review and optimize this logic
    records = []
    for user in users:
        total_spent = Record.objects.filter(purchaser=user).aggregate(Sum("price"))[
            "price__sum"
        ]
        records.append({"user": user, "total_spent": total_spent})

    context = {
        "home_active": "active",
        "home_disabled": "disabled",
        "records": records,
        "w_sum": w_sum,
        "w_price": w_price,
        "w_pp": w_pp,
        "electricity": electricity,
        "e_pp": e_pp,
        "e_days_left": e_days_left,
        "maid": maid,
        "m_pp": m_pp,
        "m_days_left": m_days_left,
    }

    return render(request, "core/index.html", context)


# TODO: Update wording and doc for view template
class AboutTemplateView(TemplateView):
    template_name = "core/about.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "about_active": "active",
                "about_disabled": "disabled",
            }
        )
        return context


class FeedbackCreateView(SuccessMessageMixin, CreateView):
    form_class = FeedbackFrom
    success_url = reverse_lazy("home")
    template_name = "core/feedback.html"
    success_message = "Thank you for your valuable feedback, it will help us to improve your experience."

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "feedback_active": "active",
                "feedback_disabled": "disabled",
            }
        )
        return context


class UserLoginView(SuccessMessageMixin, LoginView):
    authentication_form = LoginForm
    template_name = "core/login.html"
    redirect_authenticated_user = True
    success_message = "Logged In Successfully !!"
    extra_context = {
        "login_active": "active",
        "login_disabled": "disabled",
    }


class UserLogout(LogoutView):
    next_page = "home"
    success_message = "Logged Out Successfully !!"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "Logged Out Successfully !!")
        return response


# TODO: Create custom template or redirect password done view to home
class MyPasswordResetCompleteView(PasswordResetCompleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = "/login/"
        return context
