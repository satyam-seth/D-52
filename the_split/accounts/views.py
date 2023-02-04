from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView, View

from accounts.forms import GroupCreateForm, GroupJoinForm, LoginForm, SignUpForm

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


class UserSignUpView(SuccessMessageMixin, CreateView):
    form_class = SignUpForm
    success_message = "Account Created Successfully !!"
    success_url = reverse_lazy("accounts:group")
    template_name = "accounts/signup.html"
    extra_context = {
        "signup_active": "active",
        "signup_disabled": "disabled",
    }

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        valid = super().form_valid(form)

        # Login the user
        login(self.request, self.object)
        return valid


class GroupTemplateView(LoginRequiredMixin, TemplateView):
    """
    This view is used to display the group template
    which contains the links to join or create a group
    """

    template_name = "accounts/group.html"


class GroupJoinView(LoginRequiredMixin, FormView):
    """
    This view is used to display the group join form
    and join the user to the group
    """

    form_class = GroupJoinForm
    template_name = "accounts/group_join.html"
    success_url = reverse_lazy("core:home")

    def form_valid(self, form: GroupJoinForm) -> HttpResponse:
        group_name = form.cleaned_data["group_name"]
        group = Group.objects.get(name=group_name)
        # TODO: Notify the group admin and members that a new user has joined the group
        messages.success(
            self.request, f"You have joined the group {group_name} successfully !!"
        )
        # add the user to the group
        self.request.user.groups.add(group)
        return super().form_valid(form)


class GroupCreateView(LoginRequiredMixin, View):
    allowed_methods = ["POST"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save()
            print(group)
            request.user.groups.add(group)
            print(request.user.groups)
            messages.success(request, "Group created successfully !!")
            return redirect("core:home")
        else:
            messages.error(request, "Invalid group name !!")
            return redirect("accounts:group")


# TODO: Create custom template or redirect password done view to home
class MyPasswordResetCompleteView(PasswordResetCompleteView):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["login_url"] = "/login/"
        return context
