from datetime import datetime, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import localtime, make_aware, now

from accounts.models import Room
from records.forms import RecordForm, WaterForm
from records.models import Record, Water

User = get_user_model()


class TestRecordForm(TestCase):
    """Test Record Form"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email="test@user1.com",
            password="test-password",
            first_name="test",
            last_name="user1",
        )
        self.user2 = User.objects.create_user(
            email="test@user2.com",
            password="test-password",
            first_name="test",
            last_name="user2",
        )
        self.room = Room.objects.create(name="test-room", admin=self.user1)

    @patch("records.forms.now")
    def test_record_form_fields(self, mock_now):
        """Test record form fields"""

        # set mock now return value
        mock_now.return_value = make_aware(datetime(2025, 2, 16, 10, 30))

        form = RecordForm()

        # assert meta class
        self.assertEqual(form.Meta.model, Record)
        self.assertEqual(
            form.Meta.fields,
            ["purchase_datetime", "purchaser", "item", "price"],
        )

        # assert purchase_date field
        # TODO: fix this assertion
        # self.assertEqual(
        #     form.Meta.widgets["purchase_datetime"].attrs["type"],
        #     "datetime-local",
        # )
        self.assertEqual(
            form.Meta.widgets["purchase_datetime"].attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.Meta.widgets["purchase_datetime"].attrs["min"],
            localtime(
                now() - timedelta(days=form.Meta.model.max_allowed_past_days)
            ).strftime("%Y-%m-%dT%H:%M"),
        )
        self.assertEqual(
            form.Meta.widgets["purchase_datetime"].attrs["max"],
            localtime(now()).strftime("%Y-%m-%dT%H:%M"),
        )
        self.assertEqual(
            form.Meta.widgets["purchase_datetime"].attrs["value"],
            localtime(now()).strftime("%Y-%m-%dT%H:%M"),
        )

        # assert purchase_date purchaser
        self.assertEqual(
            form.Meta.widgets["purchaser"].attrs["class"],
            "form-control",
        )

        # assert item purchaser
        self.assertEqual(
            form.Meta.widgets["item"].attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.Meta.widgets["item"].attrs["placeholder"],
            "Enter item name",
        )

        # assert item price
        self.assertEqual(
            form.Meta.widgets["price"].attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.Meta.widgets["price"].attrs["placeholder"],
            "Enter item price",
        )
        self.assertEqual(
            form.Meta.widgets["price"].attrs["min"],
            "0",
        )
        self.assertEqual(
            form.Meta.widgets["price"].attrs["max"],
            "100000",
        )

    def test_purchaser_field_queryset(self):
        """Test purchaser field queryset"""

        form = RecordForm(room_id=self.room.id)
        queryset = form.fields["purchaser"].queryset
        self.assertQuerysetEqual(
            queryset,
            User.objects.filter(room_membership__room=self.room),
        )

    def test_purchaser_field_queryset_no_room(self):
        """Test purchaser field queryset no room"""

        form = RecordForm()
        queryset = form.fields["purchaser"].queryset
        self.assertQuerysetEqual(queryset, User.objects.all(), ordered=False)

    def test_record_form_working(self):
        """Test record form working"""

        # initialize form data
        form_data = {
            "purchase_datetime": timezone.now(),
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": 1234.56,
        }

        form = RecordForm(data=form_data)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a record
        record = form.save(commit=False)
        record.room = self.room
        record.adder = self.user1
        record.save()
        self.assertIsInstance(record, Record)
        self.assertEqual(
            record.purchase_datetime,
            form_data["purchase_datetime"],
        )
        self.assertEqual(record.purchaser.id, form_data["purchaser"])
        self.assertEqual(record.item, form_data["item"])
        self.assertEqual(float(record.price), form_data["price"])

    def test_record_form_valid_for_room_with_valid_purchaser(self):
        """Test record form valid for room valid purchaser"""

        # initialize form data
        form_data = {
            "purchase_datetime": timezone.now(),
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": 1234.56,
        }

        form = RecordForm(room_id=self.room.id, data=form_data)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

    def test_record_form_invalid_for_room_with_invalid_purchaser(self):
        """Test record form valid for room valid purchaser"""

        # initialize form data
        form_data = {
            "purchase_datetime": timezone.now(),
            "purchaser": self.user2.pk,
            "item": "test-item",
            "price": 1234.56,
        }

        form = RecordForm(room_id=self.room.id, data=form_data)

        # assert form is valid for valid form data
        self.assertFalse(form.is_valid())

    def test_record_form_for_negative_price(self) -> None:
        """Test record form for negative price"""

        # initialize form data
        form_data = {
            "purchase_datetime": timezone.now(),
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": -10,
        }

        form = RecordForm(room_id=self.room.id, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Ensure this value is greater than or equal to 0.",
            form.errors["price"],
        )

    def test_record_form_for_price_grater_than_100000(self) -> None:
        """Test record form for price grater than 100000"""

        # initialize form data
        form_data = {
            "purchase_datetime": timezone.now(),
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": 200000,
        }

        form = RecordForm(room_id=self.room.id, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Ensure this value is less than or equal to 100000.",
            form.errors["price"],
        )

    def test_record_form_invalid_for_feature_purchase_datetime(self) -> None:
        """Test record form invalid for feature purchaser datetime"""

        future_datetime = timezone.now() + timedelta(days=1)

        # initialize form data
        form_data = {
            "purchase_datetime": future_datetime,
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": 20,
        }

        form = RecordForm(room_id=self.room.id, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The date and time cannot be in the future.",
            form.errors["purchase_datetime"],
        )

    def test_record_form_invalid_for_too_far_in_past_purchase_datetime(self) -> None:
        """Test record form invalid for too far in past purchaser datetime"""

        too_far_in_past_datetime = timezone.now() - timedelta(days=7)

        # initialize form data
        form_data = {
            "purchase_datetime": too_far_in_past_datetime,
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": 20,
        }

        form = RecordForm(room_id=self.room.id, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The date and time must be within the last 6 days.",
            form.errors["purchase_datetime"],
        )


class TestWaterForm(TestCase):
    """Test Water Form"""

    @patch("records.forms.now")
    def test_water_form_fields(self, mock_now):
        """Test water form fields"""

        # set mock now return value
        mock_now.return_value = make_aware(datetime(2025, 2, 16, 10, 30))

        form = WaterForm()

        # assert meta class
        self.assertEqual(form.Meta.model, Water)
        self.assertEqual(form.Meta.fields, ["purchase_datetime", "quantity"])

        # assert purchase_datetime field
        # TODO: fix this assertion
        # self.assertEqual(
        #     form.Meta.widgets["purchase_datetime"].attrs["type"],
        #     "datetime-local",
        # )
        self.assertEqual(
            form.Meta.widgets["purchase_datetime"].attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.Meta.widgets["purchase_datetime"].attrs["min"],
            localtime(
                now() - timedelta(days=form.Meta.model.max_allowed_past_days)
            ).strftime("%Y-%m-%dT%H:%M"),
        )
        self.assertEqual(
            form.Meta.widgets["purchase_datetime"].attrs["max"],
            localtime(now()).strftime("%Y-%m-%dT%H:%M"),
        )
        self.assertEqual(
            form.Meta.widgets["purchase_datetime"].attrs["value"],
            localtime(now()).strftime("%Y-%m-%dT%H:%M"),
        )

        # assert quantity field
        self.assertEqual(
            form.Meta.widgets["quantity"].attrs["class"],
            "form-control",
        )

    def test_water_form_working(self):
        """Test water form working"""

        user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        room = Room.objects.create(name="test-room", admin=user)

        # initialize form data
        form_data = {
            "purchase_datetime": timezone.now(),
            "quantity": 1,
        }

        form = WaterForm(data=form_data)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a group
        water = form.save(commit=False)
        water.room = room
        self.assertIsInstance(water, Water)
        self.assertEqual(water.purchase_datetime, form_data["purchase_datetime"])
        self.assertEqual(water.quantity, form_data["quantity"])

    def test_water_form_for_quantity_less_than_1(self) -> None:
        """Test water form for quantity less than 1"""

        # initialize form data
        form_data = {
            "purchase_datetime": timezone.now(),
            "quantity": 0,
        }

        form = WaterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Ensure this value is greater than or equal to 1.",
            form.errors["quantity"],
        )

    def test_record_form_for_quantity_grater_than_5(self) -> None:
        """Test record form for quantity grater than 5"""

        # initialize form data
        form_data = {
            "purchase_datetime": timezone.now(),
            "quantity": 6,
        }

        form = WaterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Ensure this value is less than or equal to 5.",
            form.errors["quantity"],
        )

    def test_water_form_invalid_for_feature_purchase_datetime(self) -> None:
        """Test water form invalid for feature purchaser datetime"""

        future_datetime = timezone.now() + timedelta(days=1)

        # initialize form data
        form_data = {
            "purchase_datetime": future_datetime,
            "quantity": 1,
        }

        form = WaterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The date and time cannot be in the future.",
            form.errors["purchase_datetime"],
        )

    def test_water_form_invalid_for_too_far_in_past_purchase_datetime(self) -> None:
        """Test water form invalid for too far in past purchaser datetime"""

        too_far_in_past_datetime = timezone.now() - timedelta(days=7)

        # initialize form data
        form_data = {
            "purchase_datetime": too_far_in_past_datetime,
            "quantity": 1,
        }

        form = WaterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The date and time must be within the last 6 days.",
            form.errors["purchase_datetime"],
        )
