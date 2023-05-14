from accounts.forms import LoginForm, SignUpForm
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class TestLoginForm(TestCase):
    """Test Login Form"""

    def test_login_form_fields(self) -> None:
        """Test login form fields"""
        form = LoginForm()

        # assert that the form has only two fields
        self.assertEqual(len(form.fields), 2)

        # assert username field
        self.assertTrue(form.fields["username"].widget.attrs.get("autofocus"), True)
        self.assertEqual(
            form.fields["username"].widget.attrs.get("class"), "form-control"
        )

        # assert password field
        self.assertFalse(form.fields["password"].strip)  # type: ignore[attr-defined]
        self.assertEqual(form.fields["password"].label, "Password")
        self.assertEqual(
            form.fields["password"].widget.attrs.get("autocomplete"), "current-password"
        )
        self.assertEqual(
            form.fields["password"].widget.attrs.get("class"), "form-control"
        )

    # TODO: fix this test
    # def test_login_form_working(self) -> None:
    #     "Test login form working"

    #     data = {
    #         "username": "test-username",
    #         "password": "test-password",
    #     }

    #     form = LoginForm(data=data)
    #     self.assertTrue(form.is_valid())


class SignUpFormTestCase(TestCase):
    """Test SignUp Form"""

    def test_signup_form_fields(self):
        """Test signup form fields"""
        form = SignUpForm()

        # assert that the form has only two fields
        self.assertEqual(len(form.fields), 6)

        # assert field widgets
        self.assertEqual(
            form.fields["username"].widget.attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.fields["first_name"].widget.attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.fields["last_name"].widget.attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.fields["email"].widget.attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.fields["password1"].widget.attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.fields["password2"].widget.attrs["class"],
            "form-control",
        )

    def test_signup_form_working(self):
        """Test signup form working"""

        # initialize form data
        form_data = {
            "username": "test-user",
            "email": "test@example.com",
            "first_name": "test-first-name",
            "last_name": "test-last-name",
            "password1": "test-password",
            "password2": "test-password",
        }

        form = SignUpForm(data=form_data)

        # assert signup form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a user
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, form_data["username"])
        self.assertEqual(user.email, form_data["email"])
        self.assertEqual(user.first_name, form_data["first_name"])
        self.assertEqual(user.last_name, form_data["last_name"])
