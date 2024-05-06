from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from django.db import models


class UserManager(BaseUserManager):
    """Model manager for User model"""

    use_in_migrations = True

    # TODO: make first_name and last_name required
    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""

        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class RoomInvitationManager(models.Manager):
    """Model manager for RoomInvitation model"""

    def __init__(self):
        super().__init__()
        # TODO: keep the salt used in production secret!
        # self.salt = secrets.token_bytes(16).hex()
        self.salt = "c603df19008728cab0791fab1aec6f2f"

    def _get_payload_for_instance(self, invitation):
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

    def _unsigned_token(self, token: str):
        """Verify the signed token and return the invitation"""

        signer = Signer(salt=self.salt)
        return signer.unsign_object(token)

    def send_invitation(self, room, email: str):
        """Create and send an invitation to join the specified room"""

        invitation = self.create(room=room, email=email)
        token = self._generate_signed_token(invitation=invitation)

        # TODO: generate url and send email
        return invitation

    def accept_invitation(self, current_user, token: str) -> None:
        """Accept the invitation for the current user using the token"""
        payload = self._unsigned_token(token=token)

        if payload.get("email") != current_user.email:
            raise ValidationError("Invitation token is not for the current user")

        try:
            invitation = self.model.objects.get(id=payload.get("id"))
            invitation.accept()
        except self.model.DoesNotExist as e:
            raise ValidationError("Invitation not found") from e
