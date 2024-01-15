from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import localtime, now

from records.forms import RecordFrom, WaterFrom
from records.models import Record, Water

User = get_user_model()


class TestRecordForm(TestCase):
    """Test Record Form"""

    def test_record_form_fields(self):
        """Test water form fields"""

        form = RecordFrom()

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
            "5000",
        )

    def test_record_form_working(self):
        """Test record form working"""

        user = User.objects.create(username="test-user", password="test-password")

        # initialize form data
        form_data = {
            "purchase_date": "2023-05-16",
            "purchaser": user.pk,
            "item": "test-item",
            "price": 1234.56,
        }

        form = RecordFrom(data=form_data)

        print(form.errors)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a group
        record = form.save()
        self.assertIsInstance(record, Record)
        self.assertEqual(
            record.purchase_date.strftime("%Y-%m-%d"),
            form_data["purchase_date"],
        )
        self.assertEqual(record.purchaser.id, form_data["purchaser"])
        self.assertEqual(record.item, form_data["item"])
        self.assertEqual(float(record.price), form_data["price"])


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
            "purchase_date": "2023-05-15",
            "quantity": 1,
        }

        form = WaterFrom(data=form_data)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a group
        water = form.save()
        self.assertIsInstance(water, Water)
        self.assertEqual(
            water.purchase_date.strftime("%Y-%m-%d"),
            form_data["purchase_date"],
        )
        self.assertEqual(water.quantity, form_data["quantity"])
