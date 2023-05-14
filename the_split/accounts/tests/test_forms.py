from django.test import TestCase
from accounts.forms import LoginForm

from django.test.client import RequestFactory

rf = RequestFactory()


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
    #     "Test expense form valid data"

    #     data = {
    #         "username": "test-username",
    #         "password": "test-password",
    #     }

    #     form = LoginForm(data=data)

    #     self.assertTrue(form.is_valid())
