from typing import Dict, Any
from data.models import Record, Water
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView, CreateView
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.views import PasswordResetCompleteView
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import FeedbackFrom, LoginForm
from .models import Electricity, Feedback, Maid

User = get_user_model()


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
    # TODO: remove hardcoded url use url name
    success_url = "/"
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


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = LoginForm(request=request, data=request.POST)
            if form.is_valid():
                uname = form.cleaned_data["username"]
                upass = form.cleaned_data["password"]
                user = authenticate(username=uname, password=upass)
                if user is not None:
                    login(request, user)
                messages.success(request, "Logged In Successfully !!")
                return redirect("home")
        else:
            form = LoginForm()
        context = {"form": form, "login_active": "active", "login_disabled": "disabled"}
        return render(request, "core/login.html", context)
    else:
        return redirect("home")


def user_logout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully !!")
    return redirect("home")


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = "/login/"
        return context
