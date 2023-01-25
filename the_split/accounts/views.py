from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import LoginForm, SignUpForm

# Create your views here.
# TODO: Add profile view and profile edit view


class UserLoginView(SuccessMessageMixin, LoginView):
    authentication_form = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    success_message = "Logged In Successfully !!"
    extra_context = {
        "login_active": "active",
        "login_disabled": "disabled",
    }


class UserLogoutView(LogoutView):
    next_page = "core:home"
    success_message = "Logged Out Successfully !!"

    def dispatch(self, request, *args: Any, **kwargs: Any) -> Any:
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "Logged Out Successfully !!")
        return response


class UserSignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/signup.html"
    extra_context = {
        "signup_active": "active",
        "signup_disabled": "disabled",
    }


# TODO: Create custom template or redirect password done view to home
class MyPasswordResetCompleteView(PasswordResetCompleteView):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["login_url"] = "/login/"
        return context
