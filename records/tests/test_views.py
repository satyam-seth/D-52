from http import HTTPStatus
from typing import Type
from unittest import mock

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.contrib.sessions.backends.base import SessionBase
from django.core.handlers.wsgi import WSGIRequest
from django.test import Client, RequestFactory, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, TemplateView, View

from accounts.mixins import RoomRequiredMixin
from accounts.models import Room, RoomMembership
from records.forms import RecordForm, WaterFrom
from records.models import Record, Water
from records.views import (
    AddDataView,
    DownloadTemplateView,
    RecordListView,
    SearchListView,
    UserRecordListView,
    WaterListView,
)

User = get_user_model()


class TestAddDataView(TestCase):
    """Test add data view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:add_data")
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )
        self.room = Room.objects.create(name="test-room", admin=self.user)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # login user
        self.client.login(email="test@user.com", password="test-password")

    def get_mock_request(self) -> WSGIRequest:
        """To get mock request factory"""

        factory = RequestFactory()
        request = factory.get(self.url)
        request.user = self.user
        request.session = SessionBase()
        request.session["room_id"] = self.room.id
        return request

    def test_add_data_view_attributes(self) -> None:
        """Test add data view attributes"""

        # Create a mock request object
        request = self.get_mock_request()

        # Create view instance
        view = AddDataView(request=request)

        # Assertions
        self.assertIsInstance(view, View)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomRequiredMixin)

    def test_get_room_working(self) -> None:
        """Test get_room working"""

        request = self.get_mock_request()
        view = AddDataView(request=request)
        room = view.get_room()

        # Assertion
        self.assertEqual(room, self.room)

    def test_get_record_form_working(self) -> None:
        """Test get_record for working"""

        request = self.get_mock_request()
        view = AddDataView(request=request)
        record_form = view.get_record_form(self.room)

        # Assertions
        self.assertIsInstance(record_form, RecordForm)
        self.assertEqual(record_form.label_suffix, "")
        self.assertEqual(record_form.room, self.room)
        self.assertEqual(record_form.initial, {"purchaser": request.user})

    def test_get_water_form_working(self) -> None:
        """Test get_water for working"""

        view = AddDataView()
        water_form = view.get_water_form()

        # Assertions
        self.assertIsInstance(water_form, WaterFrom)
        self.assertEqual(water_form.label_suffix, "")

    @mock.patch("records.views.AddDataView.get_water_form")
    @mock.patch("records.views.AddDataView.get_record_form")
    def test_get_context_with_forms(
        self,
        mock_get_record_form,
        mock_get_water_form,
    ) -> None:
        """Test get_context_data with forms"""

        # Prepare mock data
        record_form = mock.MagicMock(spec=RecordForm)
        water_form = mock.MagicMock(spec=WaterFrom)
        mock_get_record_form.return_value = record_form
        mock_get_water_form.return_value = water_form

        # Call get_context method
        request = self.get_mock_request()
        view = AddDataView(request=request)
        context = view.get_context(
            room=self.room,
            record_form=record_form,
            water_form=water_form,
        )

        # Assertions
        mock_get_record_form.assert_not_called()
        mock_get_water_form.assert_not_called()

        self.assertEqual(context["add_active"], "active")
        self.assertEqual(context["record_form"], record_form)
        self.assertEqual(context["water_form"], water_form)


class TestRecordListView(TransactionTestCase):
    """Test record list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:records")
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        self.room = Room.objects.create(name="test-room", admin=self.user)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # login user
        self.client.login(email="test@user.com", password="test-password")

    def test_record_list_view_attributes(self) -> None:
        "Test record list view attributes"

        view = RecordListView()
        self.assertIsInstance(view, ListView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomRequiredMixin)
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
            adder=self.user,
            room=self.room,
        )

        # Make a GET request to the view
        response = self.client.get(self.url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/record_list.html")

        # Check that the records are present in the context
        records = response.context["record_list"]
        self.assertQuerysetEqual(records, Record.objects.all())


class TestUserRecordListView(TestCase):
    """Test user record list view"""

    def setUp(self) -> None:
        self.client = Client()
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
        self.url = reverse("records:detailed", kwargs={"user_id": self.user1.pk})
        self.room = Room.objects.create(name="test-room", admin=self.user1)
        RoomMembership.objects.create(room=self.room, member=self.user2)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # login user
        self.client.login(email="test@user1.com", password="test-password")

    def test_record_list_view_attributes(self) -> None:
        "Test user record list view attributes"

        view = UserRecordListView()
        self.assertIsInstance(view, ListView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomRequiredMixin)
        self.assertEqual(view.model, Record)
        self.assertEqual(view.paginate_by, 20)
        self.assertEqual(view.paginate_orphans, 10)
        self.assertEqual(view.ordering, ["-purchase_date"])

    def test_user_record_list_view_working(self) -> None:
        """Test user record list view working"""

        # Create some records
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            item="Test Item 1",
            price=123.45,
            purchaser=self.user1,
            adder=self.user1,
            room=self.room,
        )
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            item="Test Item 2",
            price=123.45,
            purchaser=self.user2,
            adder=self.user2,
            room=self.room,
        )

        # Make a GET request to the view
        response = self.client.get(self.url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/record_list.html")

        # Check that the records purchased by user1 are present in the context
        records = response.context["record_list"]
        self.assertQuerysetEqual(records, Record.objects.filter(item="Test Item 1"))
        self.assertTrue(all(record.purchaser == self.user1 for record in records))


class TestWaterListView(TransactionTestCase):
    """Test water list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:detailed_water")
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )
        self.room = Room.objects.create(name="test-room", admin=self.user)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # login user
        self.client.login(email="test@user.com", password="test-password")

    def test_water_list_view_attributes(self) -> None:
        "Test water list view attributes"

        view = WaterListView()
        self.assertIsInstance(view, ListView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomRequiredMixin)
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
        self.assertQuerysetEqual(waters, Water.objects.all())


class TestReportView(TestCase):
    """Test report view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:report")

        # TODO: remove group logic
        # create group named "d52"
        group = Group.objects.create(name="d52")

        # Create test users and add them to the "d52" group
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
        self.user1.groups.add(group)
        self.user2.groups.add(group)

        # Create room
        self.room = Room.objects.create(name="test-room", admin=self.user1)
        RoomMembership.objects.create(room=self.room, member=self.user2)

        # Create some test records
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            purchaser=self.user1,
            adder=self.user1,
            price=10,
            room=self.room,
        )
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            purchaser=self.user1,
            adder=self.user1,
            price=30,
            room=self.room,
        )
        Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            purchaser=self.user2,
            adder=self.user2,
            price=70,
            room=self.room,
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


class TestSearchListView(TransactionTestCase):
    """Test search list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:search")
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )
        self.room = Room.objects.create(name="test-room", admin=self.user)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # login user
        self.client.login(email="test@user.com", password="test-password")

    def test_search_list_view_attributes(self) -> None:
        """Test search list view attributes"""

        view = SearchListView()
        self.assertIsInstance(view, ListView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomRequiredMixin)
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
            adder=self.user,
            room=self.room,
        )
        second_record = Record.objects.create(
            purchase_date=timezone.localdate(timezone.now()),
            item="Test Item Good 2",
            price=123.45,
            purchaser=self.user,
            adder=self.user,
            room=self.room,
        )

        # Make a GET request to the view
        response = self.client.get(self.url, {"query": "good"})

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/search.html")

        # Check that the records contain item "item" are present in the context
        records = response.context["record_list"]
        self.assertQuerysetEqual(
            records, Record.objects.filter(item="Test Item Good 2")
        )
        self.assertEqual(records[0], second_record)


class TestDownloadTemplateView(TestCase):
    """Test download template view"""

    def setUp(self) -> None:
        self.client = Client()
        self.group = Group.objects.create(name="d52")
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )
        self.user.groups.add(self.group)
        self.url = reverse("records:download")
        self.room = Room.objects.create(name="test-room", admin=self.user)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # login user
        self.client.login(email="test@user.com", password="test-password")

    def test_download_template_view_attributes(self) -> None:
        """Test download template view attributes"""

        view = DownloadTemplateView()
        self.assertIsInstance(view, TemplateView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomRequiredMixin)
        self.assertTrue(view.template_name, "records/download.html")

    def test_download_template_view_working(self) -> None:
        """Test download template view working"""

        # get group users
        users = User.objects.filter(groups__in=[self.group])

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
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
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
        expected_filename = f"{self.user.get_full_name()} Items Records.xls"
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
