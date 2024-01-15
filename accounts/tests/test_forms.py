from accounts.forms import GroupCreateForm, GroupJoinForm, LoginForm, SignUpForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
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


class TestSignUpForm(TestCase):
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

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a user
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, form_data["username"])
        self.assertEqual(user.email, form_data["email"])
        self.assertEqual(user.first_name, form_data["first_name"])
        self.assertEqual(user.last_name, form_data["last_name"])


class TestGroupJoinForm(TestCase):
    """Test Group Join Form"""

    def test_group_join_form_field(self) -> None:
        """test group join form field"""

        form = GroupJoinForm()

        # assert that the form has only one field
        self.assertEqual(len(form.fields), 1)

        # assert field widget
        self.assertEqual(form.fields["group_name"].label, "Group Name:")
        self.assertEqual(
            form.fields["group_name"].widget.attrs["class"], "form-control"
        )
        self.assertEqual(
            form.fields["group_name"].help_text, "Enter the group name to join"
        )

    def test_group_join_from_working_for_valid_group_name(self):
        """Test group join form is working for valid group name"""

        group_name = "test-group"

        # create group
        Group.objects.create(name=group_name)

        # initialize form data
        form_data = {
            "group_name": group_name,
        }

        form = GroupJoinForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["group_name"], group_name)

    def test_group_join_from_working_for_invalid_group_name(self):
        """Test group join form is working for invalid group name"""

        group_name = "test-group"

        # initialize form data
        form_data = {
            "group_name": group_name,
        }

        form = GroupJoinForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("group_name", form.errors)
        self.assertEqual(
            form.errors["group_name"],
            [f"group with name {group_name} is not found"],
        )


class TestGroupCreateForm(TestCase):
    """Test Group Create Form"""

    def test_group_create_form_field(self) -> None:
        """test group create form field"""

        form = GroupCreateForm()

        self.assertEqual(form.Meta.model, Group)
        self.assertEqual(form.Meta.fields, ("name",))
        self.assertEqual(form.Meta.labels["name"], "Group Name:")
        self.assertEqual(
            form.Meta.widgets["name"].attrs["class"],
            "form-control",
        )

    def test_group_create_form_working(self):
        """Test group create form working"""

        # initialize form data
        form_data = {"name": "test-group"}

        form = GroupCreateForm(data=form_data)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a group
        group = form.save()
        self.assertIsInstance(group, Group)