from django.test import TestCase
from django.utils.timezone import localtime, now, timedelta
from records.forms import WaterFrom
from records.models import Water


class WaterFormTestCase(TestCase):
    """Test Water Form"""

    def test_water_form_fields(self):
        """test water form fields"""

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
            "purchase_date": localtime(now()).date(),
            "quantity": 1,
        }

        form = WaterFrom(data=form_data)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a group
        water = form.save()
        self.assertIsInstance(water, Water)
