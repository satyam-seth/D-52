from typing import Any

from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from django.db import models

from accounts.types import RoomInvitationTokenPayload


class UserManager(BaseUserManager):
    """Model manager for User model"""

    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        **extra_fields: Any,
    ):
        """Create and save a User with the given email and password."""

        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        **extra_fields: Any,
    ):
        """Create and save a regular User with the given email and password."""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(
            email,
            password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )

    def create_superuser(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        **extra_fields: Any,
    ):
        """Create and save a SuperUser with the given email and password."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, first_name, last_name, **extra_fields)


class RoomInvitationManager(models.Manager):
    """Model manager for RoomInvitation model"""

    def __init__(self):
        super().__init__()
        # TODO: keep the salt used in production secret!
        # self.salt = secrets.token_bytes(16).hex()
        self.salt = "c603df19008728cab0791fab1aec6f2f"

    def _get_payload_for_instance(self, invitation) -> RoomInvitationTokenPayload:
        """Construct payload for instance to generate signed token"""

        return {
            "id": invitation.id,
            "room": invitation.room.id,
            "email": invitation.email,
        }

    def _generate_signed_token(self, invitation) -> str:
        """Generate a signed token using the invitation and salt"""

        signer = Signer(salt=self.salt)
        payload = self._get_payload_for_instance(invitation)
        return signer.sign_object(payload)

    def unsigned_token(self, token: str) -> RoomInvitationTokenPayload:
        """Verify the signed token and return the invitation"""

        signer = Signer(salt=self.salt)
        return signer.unsign_object(token)

    def send_invitation(self, room, email: str, absolute_invitation_url: str):
        """Create and send an invitation to join the specified room"""

        invitation = self.create(room=room, email=email)
        token = self._generate_signed_token(invitation=invitation)

        invitation_url = f"{absolute_invitation_url}?token={token}"

        print(invitation_url)

        # TODO: send email
        return invitation

    def accept_invitation(self, current_user, token: str) -> None:
        """Accept the invitation for the current user using the token"""

        payload = self.unsigned_token(token=token)

        if payload.get("email") != current_user.email:
            raise ValidationError("Invitation token is not for the current user")

        try:
            invitation = self.model.objects.get(
                id=payload.get("id"),
                # TODO: fix status value as models choice instead of hardcoded string
                status="pending",
            )
            invitation.accept()
        except self.model.DoesNotExist as e:
            raise ValidationError("Invitation not found") from e

    def reject_invitation(self, current_user, token: str) -> None:
        """Reject the invitation for the current user using the token"""

        payload = self.unsigned_token(token=token)

        if payload.get("email") != current_user.email:
            raise ValidationError("Invitation token is not for the current user")

        try:
            invitation = self.model.objects.get(
                id=payload.get("id"),
                # TODO: fix status value as models choice instead of hardcoded string
                status="pending",
            )
            invitation.reject()
        except self.model.DoesNotExist as e:
            raise ValidationError("Invitation not found") from e
