from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView

from accounts.forms import LoginForm, ProfileUpdateForm, RoomCreateForm, SignUpForm
from accounts.models import Profile


# Create your views here.
class ProfileTemplateView(LoginRequiredMixin, TemplateView):
    """View to show user profile"""

    template_name = "accounts/profile.html"


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    """View to show user profile"""

    form_class = ProfileUpdateForm
    template_name = "accounts/profile_update.html"
    success_message = "Profile Updated !!"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form: Any) -> HttpResponse:
        # Get the current user's profile
        profile = Profile.objects.get(user=self.request.user)

        # Update the profile with the form data
        profile.avatar = form.cleaned_data["avatar"]
        profile.cover_photo = form.cleaned_data["cover_photo"]
        profile.save()
        return super().form_valid(form)


class UserLoginView(SuccessMessageMixin, LoginView):
    """View to handle user login"""

    authentication_form = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    success_message = "Logged In Successfully !!"
    extra_context = {"login_active": "active"}


class UserLogoutView(LogoutView):
    """View to handle user logout"""

    next_page = "core:home"
    success_message = "Logged Out Successfully !!"

    def dispatch(self, request, *args: Any, **kwargs: Any) -> Any:
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "Logged Out Successfully !!")
        return response


class UserSignUpView(SuccessMessageMixin, CreateView):
    """View to handle user signup"""

    form_class = SignUpForm
    success_message = "Account Created Successfully !!"
    success_url = reverse_lazy("accounts:room")
    template_name = "accounts/signup.html"
    extra_context = {"signup_active": "active"}

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        valid = super().form_valid(form)

        # Login the user
        login(self.request, self.object)
        return valid


class RoomTemplateView(LoginRequiredMixin, TemplateView):
    """
    This view is used to display the room template
    which contains the links to join or create a room
    """

    template_name = "accounts/room.html"


# class RoomJoinView(LoginRequiredMixin, FormView):
#     """
#     This view is used to display and handle the room join form
#     """

#     form_class = RoomJoinForm
#     template_name = "accounts/room_join.html"
#     success_url = reverse_lazy("core:home")

#     def form_valid(self, form: RoomJoinForm) -> HttpResponse:
#         room_id = form.cleaned_data["room_id"]
#         room = Room.objects.get(id=room_id)
#         # TODO: also update invitation status
#         # add the user to the room
#         membership = RoomMembership(user=self.request.user, room=room)

#         try:
#             membership.save()
#             # TODO: Notify the group admin and members that a new user has joined the group
#             messages.success(
#                 self.request, f"You have joined the room '{room_id}' successfully !!"
#             )
#         except IntegrityError as e:
#             print(e)
#             messages.success(
#                 self.request,
#                 f"You have already joined the room '{room_id}'",
#             )
#         return super().form_valid(form)


class RoomCreateView(LoginRequiredMixin, CreateView):
    """
    This view is used to display and handle the room create form
    """

    form_class = RoomCreateForm
    template_name = "accounts/room_create.html"
    # TODO: redirect to invite members view
    success_url = reverse_lazy("core:home")

    def form_valid(self, form: RoomCreateForm) -> HttpResponse:
        room = form.save(commit=False)
        # make current user as admin
        room.admin = self.request.user
        room.save()
        messages.success(self.request, f"Room '{room.name}' created successfully!")
        # Note: On saving, the admin user is automatically joined
        # via the Room model's post-save signal
        messages.success(
            self.request, f"You have joined the room '{room.name}' successfully !!"
        )
        return super().form_valid(form)


# TODO: Create custom template or redirect password done view to home
class MyPasswordResetCompleteView(PasswordResetCompleteView):
    """View to handle user password complete"""

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["login_url"] = "/login/"
        return context
