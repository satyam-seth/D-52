from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import localtime, now

from accounts.models import Room
from records.forms import RecordForm, WaterFrom
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

    def test_record_form_fields(self):
        """Test water form fields"""

        form = RecordForm()

        # assert meta class
        self.assertEqual(form.Meta.model, Record)
        self.assertEqual(
            form.Meta.fields, ["purchase_date", "purchaser", "item", "price"]
        )

        # assert purchase_date field
        # TODO: fix this assertion
        # self.assertEqual(
        #     form.Meta.widgets["purchase_date"].attrs["type"],
        #     "date",
        # )
        self.assertEqual(
            form.Meta.widgets["purchase_date"].attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.Meta.widgets["purchase_date"].attrs["min"],
            localtime(now() - timedelta(6)).date(),
        )
        self.assertEqual(
            form.Meta.widgets["purchase_date"].attrs["max"],
            localtime(now()).date(),
        )
        self.assertEqual(
            form.Meta.widgets["purchase_date"].attrs["value"],
            localtime(now()).date(),
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

        form = RecordForm(room=self.room)
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
            "purchase_date": timezone.now().date(),
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
            record.purchase_date,
            form_data["purchase_date"],
        )
        self.assertEqual(record.purchaser.id, form_data["purchaser"])
        self.assertEqual(record.item, form_data["item"])
        self.assertEqual(float(record.price), form_data["price"])

    def test_record_form_valid_for_room_with_valid_purchaser(self):
        """Test record form valid for room valid purchaser"""

        # initialize form data
        form_data = {
            "purchase_date": timezone.now().date(),
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": 1234.56,
        }

        form = RecordForm(room=self.room, data=form_data)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

    def test_record_form_invalid_for_room_with_invalid_purchaser(self):
        """Test record form valid for room valid purchaser"""

        # initialize form data
        form_data = {
            "purchase_date": timezone.now().date(),
            "purchaser": self.user2.pk,
            "item": "test-item",
            "price": 1234.56,
        }

        form = RecordForm(room=self.room, data=form_data)

        # assert form is valid for valid form data
        self.assertFalse(form.is_valid())

    def test_clean_price_for_valid_price(self) -> None:
        """Test clean price for valid price"""

        # initialize form data
        form_data = {
            "purchase_date": timezone.now().date(),
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": 999.99,
        }

        form = RecordForm(room=self.room, data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_price_for_negative_price(self) -> None:
        """Test clean price for negative price"""

        # initialize form data
        form_data = {
            "purchase_date": timezone.now().date(),
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": -10,
        }

        form = RecordForm(room=self.room, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Price must be between 0 and 100000.", form.errors["price"])

    def test_clean_price_for_price_grater_than_100000(self) -> None:
        """Test clean price for price grater than 100000"""

        # initialize form data
        form_data = {
            "purchase_date": timezone.now().date(),
            "purchaser": self.user1.pk,
            "item": "test-item",
            "price": 200000,
        }

        form = RecordForm(room=self.room, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Price must be between 0 and 100000.", form.errors["price"])


class TestWaterForm(TestCase):
    """Test Water Form"""

    def test_water_form_fields(self):
        """Test water form fields"""

        form = WaterFrom()

        # assert meta class
        self.assertEqual(form.Meta.model, Water)
        self.assertEqual(form.Meta.fields, ["purchase_date", "quantity"])

        # assert purchase_date field
        # TODO: fix this assertion
        # self.assertEqual(
        #     form.Meta.widgets["purchase_date"].attrs["type"],
        #     "date",
        # )
        self.assertEqual(
            form.Meta.widgets["purchase_date"].attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.Meta.widgets["purchase_date"].attrs["min"],
            localtime(now() - timedelta(20)).date(),
        )
        self.assertEqual(
            form.Meta.widgets["purchase_date"].attrs["max"],
            localtime(now()).date(),
        )
        self.assertEqual(
            form.Meta.widgets["purchase_date"].attrs["value"],
            localtime(now()).date(),
        )

        # assert quantity field
        self.assertEqual(
            form.Meta.widgets["quantity"].attrs["class"],
            "form-control",
        )

    def test_water_form_working(self):
        """Test water form working"""

        # initialize form data
        form_data = {
            "purchase_date": timezone.now().date(),
            "quantity": 1,
        }

        form = WaterFrom(data=form_data)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a group
        water = form.save()
        self.assertIsInstance(water, Water)
        self.assertEqual(water.purchase_date, form_data["purchase_date"])
        self.assertEqual(water.quantity, form_data["quantity"])
