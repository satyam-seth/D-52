from http import HTTPStatus
from typing import Type
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, TemplateView, View
from records.forms import RecordFrom, WaterFrom
from records.models import Record, Water
from records.views import (
    AddTemplateView,
    DownloadTemplateView,
    RecordAddView,
    RecordListView,
    SearchListView,
    UserRecordListView,
    WaterAddView,
    WaterListView,
)

User = get_user_model()


class TestAddTemplateView(TestCase):
    """Test add template view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:add")
        self.user = User.objects.create_user(
            username="test-user",
            password="test-password",
        )

    def test_add_template_view_attributes(self) -> None:
        """Test add template view attributes"""

        view = AddTemplateView()
        self.assertIsInstance(view, TemplateView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertTrue(view.template_name, "records/add.html")

        context = view.get_context_data()

        # Assert that the values associated with the keys are of the expected types
        self.assertIsInstance(context["add_active"], str)
        self.assertIsInstance(context["record_form"], RecordFrom)
        self.assertIsInstance(context["water_form"], WaterFrom)

    def test_add_template_view_working(self) -> None:
        """Test add template view working"""

        # login user
        self.client.login(username="test-user", password="test-password")

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/add.html")

        # Assert context is correct
        self.assertEqual(response.context["add_active"], "active")


class TestRecordAddView(TestCase):
    """Test record add view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:add_item")
        self.user = User.objects.create_user(
            username="test-user",
            password="test-password",
        )
        # login user
        self.client.login(username="test-user", password="test-password")

    def test_record_add_view_attributes(self) -> None:
        """Test record add view attributes"""

        view = RecordAddView()
        self.assertIsInstance(view, View)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertEqual(view.http_method_names, ["post"])

    def test_record_add_view_for_valid_post_data(self) -> None:
        """Test record add view working for valid post data"""

        valid_form_data = {
            "purchase_date": timezone.localdate(timezone.now()),
            "item": "Test Item",
            "price": 123.45,
            "purchaser": self.user.pk,
        }

        response = self.client.post(
            self.url,
            data=valid_form_data,
        )

        # Redirects to the specified URL
        self.assertRedirects(response, reverse("records:add"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Assert success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(str(messages[0]), "Your item record successfully added.")

        # Assert that the record is saved in the database
        self.assertEqual(Record.objects.count(), 1)
        record: Type[Record] = Record.objects.first()  # type: ignore
        self.assertEqual(record.item, valid_form_data["item"])
        self.assertEqual(float(str(record.price)), valid_form_data["price"])
        self.assertEqual(record.purchaser, self.user)
        self.assertEqual(record.purchase_date, valid_form_data["purchase_date"])
        self.assertEqual(record.adder, self.user)

    def test_record_add_view_for_invalid_post_data(self) -> None:
        """Test record add view working for invalid post data"""

        valid_form_data = {
            "item": "Test Item",
        }

        response = self.client.post(
            self.url,
            data=valid_form_data,
        )

        # Redirects to the specified URL
        self.assertRedirects(response, reverse("records:add"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Assert success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(
            str(messages[0]),
            "Please check and fill all information correctly, Your item record not added.",
        )

        # Assert that the record is not saved in the database
        self.assertEqual(Record.objects.count(), 0)


class TestWaterAddView(TestCase):
    """Test water add view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:add_water")
        self.user = User.objects.create_user(
            username="test-user",
            password="test-password",
        )
        # login user
        self.client.login(username="test-user", password="test-password")

    def test_water_add_view_attributes(self) -> None:
        """Test water add view attributes"""

        view = WaterAddView()
        self.assertIsInstance(view, View)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertEqual(view.http_method_names, ["post"])

    def test_water_add_view_for_valid_post_data(self) -> None:
        """Test water add view working for valid post data"""

        valid_form_data = {
            "purchase_date": timezone.localdate(timezone.now()),
            "quantity": 1,
        }

        response = self.client.post(
            self.url,
            data=valid_form_data,
        )

        # Redirects to the specified URL
        self.assertRedirects(response, reverse("records:add"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Assert success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(str(messages[0]), "Water record successfully added.")

        # Assert that the water is saved in the database
        self.assertEqual(Water.objects.count(), 1)
        water: Type[Water] = Water.objects.first()  # type: ignore
        self.assertEqual(water.quantity, valid_form_data["quantity"])
        self.assertEqual(water.purchase_date, valid_form_data["purchase_date"])
        self.assertEqual(water.adder, self.user)

    def test_water_add_view_for_invalid_post_data(self) -> None:
        """Test water add view working for invalid post data"""

        valid_form_data = {
            "quantity": 1,
        }

        response = self.client.post(
            self.url,
            data=valid_form_data,
        )

        # Redirects to the specified URL
        self.assertRedirects(response, reverse("records:add"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Assert success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(
            str(messages[0]),
            "Please check and fill all information correctly, Water record not added.",
        )

        # Assert that the water is not saved in the database
        self.assertEqual(Water.objects.count(), 0)


class TestRecordListView(TestCase):
    """Test record list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:records")
        self.user = User.objects.create_user(
            username="test-user", password="test-password"
        )

    def test_record_list_view_attributes(self) -> None:
        "Test record list view attributes"

        view = RecordListView()
        self.assertIsInstance(view, ListView)
        self.assertEqual(view.model, Record)
        self.assertEqual(view.paginate_by, 20)
        self.assertEqual(view.paginate_orphans, 10)
        self.assertEqual(view.ordering, ["-purchase_date"])
        self.assertEqual(view.extra_context, {"records_active": "active"})

    def test_record_list_view_working(self) -> None:
        """Test record list view working"""

        # Create a record
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            item="Test Item",
            price=123.45,
            purchaser=self.user,
        )

        # Make a GET request to the view
        response = self.client.get(self.url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/record_list.html")

        # Check that the records are present in the context
        records = response.context["record_list"]
        self.assertEqual(records.count(), 1)


class TestUserRecordListView(TestCase):
    """Test user record list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="test-user-1", password="test-password"
        )
        self.user2 = User.objects.create_user(
            username="test-user-2", password="test-password"
        )
        self.url = reverse("records:detailed", kwargs={"user_id": self.user1.pk})

    def test_record_list_view_attributes(self) -> None:
        "Test user record list view attributes"

        view = UserRecordListView()
        self.assertIsInstance(view, ListView)
        self.assertEqual(view.model, Record)
        self.assertEqual(view.paginate_by, 20)
        self.assertEqual(view.paginate_orphans, 10)

    def test_user_record_list_view_working(self) -> None:
        """Test user record list view working"""

        # Create some records
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            item="Test Item 1",
            price=123.45,
            purchaser=self.user1,
        )
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            item="Test Item 2",
            price=123.45,
            purchaser=self.user2,
        )

        # Make a GET request to the view
        response = self.client.get(self.url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/record_list.html")

        # Check that the records purchased by user1 are present in the context
        records = response.context["record_list"]
        self.assertEqual(records.count(), 1)
        self.assertTrue(all(record.purchaser == self.user1 for record in records))


class TestWaterListView(TestCase):
    """Test water list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:detailed_water")
        self.user = User.objects.create_user(
            username="test-user",
            password="test-password",
        )

    def test_water_list_view_attributes(self) -> None:
        "Test water list view attributes"

        view = WaterListView()
        self.assertIsInstance(view, ListView)
        self.assertEqual(view.model, Water)
        self.assertEqual(view.paginate_by, 20)
        self.assertEqual(view.paginate_orphans, 10)
        self.assertEqual(view.ordering, ["-purchase_date"])

    def test_water_list_view_working(self) -> None:
        """Test water list view working"""

        # Create a water record
        Water.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            quantity=1,
        )

        # Make a GET request to the view
        response = self.client.get(self.url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/water_list.html")

        # Check that the water records are present in the context
        waters = response.context["water_list"]
        self.assertEqual(waters.count(), 1)


class TestReportView(TestCase):
    """Test report view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:report")

        # create group named "d52"
        group = Group.objects.create(name="d52")

        # Create test users and add them to the "d52" group
        self.user1 = User.objects.create_user(
            username="test-user-1",
            password="test-password",
        )
        self.user2 = User.objects.create_user(
            username="test-user-2",
            password="test-password",
        )
        self.user1.groups.add(group)
        self.user2.groups.add(group)

        # Create some test records
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            purchaser=self.user1,
            price=10,
        )
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            purchaser=self.user1,
            price=30,
        )
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            purchaser=self.user2,
            price=70,
        )

    def test_report_view_working(self) -> None:
        """Test report view working"""

        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the expected context variables are present in the response
        self.assertEqual(response.context["report_active"], "active")
        self.assertEqual(response.context["total_records"].count(), 3)
        self.assertEqual(response.context["total_price"], 110)
        self.assertEqual(response.context["per_user_price"], 55)
        self.assertEqual(response.context["each_user_records"][1]["price_diff"], -15)
        self.assertEqual(response.context["each_user_records"][1]["total_spent"], 70)
        self.assertEqual(response.context["each_user_records"][1]["user"], self.user2)


class TestSearchListView(TestCase):
    """Test search list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:search")
        self.user = User.objects.create_user(
            username="test-user",
            password="test-password",
        )

    def test_search_list_view_attributes(self) -> None:
        """Test search list view attributes"""

        view = SearchListView()
        self.assertIsInstance(view, ListView)
        self.assertEqual(view.model, Record)
        self.assertEqual(view.paginate_by, 20)
        self.assertEqual(view.paginate_orphans, 10)
        self.assertEqual(view.template_name, "records/search.html")

    def test_search_list_view_working(self) -> None:
        """Test search list view working"""

        # Create some records
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            item="Test Item 1",
            price=123.45,
            purchaser=self.user,
        )
        second_record = Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            item="Test Item Good 2",
            price=123.45,
            purchaser=self.user,
        )

        # Make a GET request to the view
        response = self.client.get(self.url, {"query": "good"})

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/search.html")

        # Check that the records contain item "item" are present in the context
        records = response.context["record_list"]
        self.assertEqual(records.count(), 1)
        self.assertEqual(records[0], second_record)


class TestDownloadTemplateView(TestCase):
    """Test download template view"""

    def setUp(self) -> None:
        self.client = Client()
        self.group = Group.objects.create(name="d52")
        self.user = User.objects.create_user(
            username="test-user",
            password="test-password",
        )
        self.user.groups.add(self.group)
        self.url = reverse("records:download")

    def test_download_template_view_attributes(self) -> None:
        """Test download template view attributes"""

        view = DownloadTemplateView()
        self.assertIsInstance(view, TemplateView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertTrue(view.template_name, "records/download.html")

    def test_download_template_view_working(self) -> None:
        """Test download template view working"""

        # get group users
        users = User.objects.filter(groups__in=[self.group])

        # login user
        self.client.login(username="test-user", password="test-password")

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/download.html")

        # Assert context is correct
        self.assertEqual(response.context["download_active"], "active")
        self.assertQuerysetEqual(response.context["users"], users)


class TestOverallXlsView(TestCase):
    """Test overall xls view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:overall_xls")

    @mock.patch("records.views.get_excel")
    def test_overall_xls_view_working(self, mock_get_excel) -> None:
        """Test overall xls view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that get_excel function is called once
        mock_get_excel.assert_called_once()

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the content type of the response is application/ms-excel
        self.assertEqual(response["Content-Type"], "application/ms-excel")

        # Assert that the content disposition is correctly set
        expected_filename = "Overall Items Records.xls"
        self.assertEqual(
            response["Content-Disposition"],
            f"attachment; filename={expected_filename}",
        )


class TestUserXlsView(TestCase):
    """Test user xls view"""

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            username="test-user",
            password="test-password",
        )
        self.url = reverse("records:user_xls", kwargs={"user_id": self.user.pk})

    @mock.patch("records.views.get_excel")
    def test_user_xls_view_working(self, mock_get_excel) -> None:
        """Test user xls view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that get_excel function is called once
        mock_get_excel.assert_called_once()

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the content type of the response is application/ms-excel
        self.assertEqual(response["Content-Type"], "application/ms-excel")

        # Assert that the content disposition is correctly set
        expected_filename = f"{self.user.username} Items Records.xls"
        self.assertEqual(
            response["Content-Disposition"],
            f"attachment; filename={expected_filename}",
        )


class TestWaterXlsView(TestCase):
    """Test water xls view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:water_xls")

    @mock.patch("records.views.get_excel")
    def test_water_xls_view_working(self, mock_get_excel) -> None:
        """Test water xls view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that get_excel function is called once
        mock_get_excel.assert_called_once()

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the content type of the response is application/ms-excel
        self.assertEqual(response["Content-Type"], "application/ms-excel")

        # Assert that the content disposition is correctly set
        expected_filename = "Water Entry Records.xls"
        self.assertEqual(
            response["Content-Disposition"],
            f"attachment; filename={expected_filename}",
        )


class TestElectricityXlsView(TestCase):
    """Test electricity xls view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:electricity_xls")

    @mock.patch("records.views.get_excel")
    def test_electricity_xls_view_working(self, mock_get_excel) -> None:
        """Test electricity xls view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that get_excel function is called once
        mock_get_excel.assert_called_once()

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the content type of the response is application/ms-excel
        self.assertEqual(response["Content-Type"], "application/ms-excel")

        # Assert that the content disposition is correctly set
        expected_filename = "Electricity Bill Records.xls"
        self.assertEqual(
            response["Content-Disposition"],
            f"attachment; filename={expected_filename}",
        )


class TestMaidXlsView(TestCase):
    """Test maid xls view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:maid_xls")

    @mock.patch("records.views.get_excel")
    def test_maid_xls_view_working(self, mock_get_excel) -> None:
        """Test maid xls view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that get_excel function is called once
        mock_get_excel.assert_called_once()

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the content type of the response is application/ms-excel
        self.assertEqual(response["Content-Type"], "application/ms-excel")

        # Assert that the content disposition is correctly set
        expected_filename = "Maid Salary Records.xls"
        self.assertEqual(
            response["Content-Disposition"],
            f"attachment; filename={expected_filename}",
        )
