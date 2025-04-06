from datetime import timedelta
from http import HTTPStatus
from io import BytesIO
from typing import Type
from unittest import mock

import pandas as pd
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.sessions.backends.base import SessionBase
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, TemplateView, View

from accounts.mixins import RoomRequiredMixin
from accounts.models import Room, RoomMembership
from records.export import RoomExporter
from records.forms import RecordForm, WaterForm
from records.models import Record, Water
from records.views import (
    AddDataView,
    BaseExportView,
    DashboardTemplateView,
    ExportDataView,
    RecordListView,
    RoomReportView,
    WaterListView,
)

User = get_user_model()


class TestDashboardTemplateView(TestCase):
    """Test dashboard template view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:dashboard")
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
        self.user3 = User.objects.create_user(
            email="test@user3.com",
            password="test-password",
            first_name="test",
            last_name="user3",
        )

        # Create room
        self.room = Room.objects.create(name="test-room", admin=self.user1)

        # Create room 1 membership for user 2
        RoomMembership.objects.create(room=self.room, member=self.user2)
        # Create room 1 membership for user 3
        RoomMembership.objects.create(room=self.room, member=self.user3)

    def get_mock_request(self) -> WSGIRequest:
        """To get mock request factory"""

        factory = RequestFactory()
        request = factory.get(self.url)
        request.user = self.user1
        request.session = SessionBase()
        request.session["room_id"] = self.room.id
        return request

    def test_dashboard_view_attributes(self) -> None:
        """Test dashboard template view attributes"""

        view = DashboardTemplateView()
        self.assertIsInstance(view, TemplateView)
        self.assertIsInstance(view, RoomRequiredMixin)
        self.assertEqual(view.template_name, "records/dashboard.html")

    def test_get_water_context(self) -> None:
        """Test get water context"""

        now = timezone.now()
        past_datetime = now - timedelta(days=2)

        # Create water records
        Water.objects.create(
            quantity=5,
            adder=self.user1,
            room=self.room,
            purchase_datetime=now,
        )
        Water.objects.create(
            quantity=2,
            adder=self.user1,
            room=self.room,
            purchase_datetime=past_datetime,
        )
        Water.objects.create(
            quantity=1,
            adder=self.user2,
            room=self.room,
            purchase_datetime=past_datetime,
        )

        # Call get water context
        request = self.get_mock_request()
        view = DashboardTemplateView(request=request)
        water_context = view.get_water_context(room_id=self.room.id)

        # Assert water context
        self.assertEqual(water_context["water_quantity"], 8)

    def test_get_water_context_for_zero_state(self) -> None:
        """Test get water context for zero state"""

        # Call get water context
        request = self.get_mock_request()
        view = DashboardTemplateView(request=request)
        water_context = view.get_water_context(room_id=self.room.id)

        # Assert water context
        self.assertEqual(water_context["water_quantity"], 0)

    def test_get_room_members_context(self):
        """Test get room members context"""

        # Create records
        Record.objects.create(
            purchase_datetime=timezone.now(),
            purchaser=self.user1,
            adder=self.user1,
            price=120,
            room=self.room,
        )
        Record.objects.create(
            purchase_datetime=timezone.now(),
            purchaser=self.user1,
            adder=self.user1,
            price=80,
            room=self.room,
        )
        Record.objects.create(
            purchase_datetime=timezone.now(),
            purchaser=self.user2,
            adder=self.user2,
            price=100,
            room=self.room,
        )

        # Call get room members context
        request = self.get_mock_request()
        view = DashboardTemplateView(request=request)
        room_members_context = view.get_room_members_context(room_id=self.room.id)

        # Assert room members context
        room_members_data = room_members_context["room_members_data"]
        self.assertEqual(len(room_members_data), 3)

        # Assertion for user 1
        self.assertEqual(room_members_data[0]["member"], self.user1)
        self.assertEqual(room_members_data[0]["records_count"], 2)
        self.assertEqual(room_members_data[0]["total_spent"], 200)

        # Assertion for user 2
        self.assertEqual(room_members_data[1]["member"], self.user2)
        self.assertEqual(room_members_data[1]["records_count"], 1)
        self.assertEqual(room_members_data[1]["total_spent"], 100)

        # Assertion for user 3
        self.assertEqual(room_members_data[2]["member"], self.user3)
        self.assertEqual(room_members_data[2]["records_count"], 0)
        self.assertEqual(room_members_data[2]["total_spent"], 0)

    def test_get_room_members_context_for_zero_state(self):
        """Test get room members context for zero state"""

        # Call get room members context
        request = self.get_mock_request()
        view = DashboardTemplateView(request=request)
        room_members_context = view.get_room_members_context(room_id=self.room.id)

        # Assert room members context
        room_members_data = room_members_context["room_members_data"]
        self.assertEqual(len(room_members_data), 3)

        # Assertion for user 1
        self.assertEqual(room_members_data[0]["member"], self.user1)
        self.assertEqual(room_members_data[0]["records_count"], 0)
        self.assertEqual(room_members_data[0]["total_spent"], 0)

        # Assertion for user 2
        self.assertEqual(room_members_data[1]["member"], self.user2)
        self.assertEqual(room_members_data[1]["records_count"], 0)
        self.assertEqual(room_members_data[1]["total_spent"], 0)

        # Assertion for user 3
        self.assertEqual(room_members_data[2]["member"], self.user3)
        self.assertEqual(room_members_data[2]["records_count"], 0)
        self.assertEqual(room_members_data[2]["total_spent"], 0)

    @mock.patch("records.views.DashboardTemplateView.get_water_context")
    @mock.patch("records.views.DashboardTemplateView.get_room_members_context")
    def test_dashboard_template_view_working(
        self,
        mock_get_room_members_context,
        mock_get_water_context,
    ):
        """Test dashboard template view working"""

        # Prepare mock data
        mock_get_water_context.return_value = {"quantity": 0}
        mock_get_room_members_context.return_value = {"room_members_data": []}

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # login user 1
        self.client.login(email="test@user1.com", password="test-password")

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/dashboard.html")

        # Assert context methods are called once with correct room id
        mock_get_water_context.called_once_with(room_id=self.room.id)
        mock_get_room_members_context.called_once_with(room_id=self.room.id)

        # Assert context is correct
        self.assertEqual(response.context["dashboard_active"], "active")
        self.assertEqual(response.context["quantity"], 0)
        self.assertEqual(response.context["room_members_data"], [])


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
        self.assertIsInstance(view, RoomRequiredMixin)

    def test_get_record_form_working(self) -> None:
        """Test get_record for working"""

        request = self.get_mock_request()
        view = AddDataView(request=request)
        record_form = view.get_record_form()

        # Assertions
        self.assertIsInstance(record_form, RecordForm)
        self.assertEqual(record_form.label_suffix, "")
        self.assertEqual(record_form.room_id, self.room.id)
        self.assertEqual(record_form.initial, {"purchaser": request.user})

    def test_get_water_form_working(self) -> None:
        """Test get_water for working"""

        view = AddDataView()
        water_form = view.get_water_form()

        # Assertions
        self.assertIsInstance(water_form, WaterForm)
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
        water_form = mock.MagicMock(spec=WaterForm)
        mock_get_record_form.return_value = record_form
        mock_get_water_form.return_value = water_form

        # Call get_context method
        request = self.get_mock_request()
        view = AddDataView(request=request)
        context = view.get_context(record_form=record_form, water_form=water_form)

        # Assertions
        mock_get_record_form.assert_not_called()
        mock_get_water_form.assert_not_called()

        self.assertEqual(context["add_active"], "active")
        self.assertEqual(context["record_form"], record_form)
        self.assertEqual(context["water_form"], water_form)

    @mock.patch("records.views.AddDataView.get_water_form")
    @mock.patch("records.views.AddDataView.get_record_form")
    def test_get_context_without_forms(
        self,
        mock_get_record_form,
        mock_get_water_form,
    ) -> None:
        """Test get_context_data without forms"""

        # Call get_context method
        request = self.get_mock_request()
        view = AddDataView(request=request)
        context = view.get_context()

        # Assertions
        mock_get_record_form.assert_called_once()
        mock_get_water_form.assert_called_once()

        self.assertEqual(context["add_active"], "active")
        self.assertEqual(context["record_form"], mock_get_record_form.return_value)
        self.assertEqual(context["water_form"], mock_get_water_form.return_value)

    def test_get_working(self) -> None:
        """Test get working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/add_data.html")

        # Assert context is correct
        self.assertEqual(response.context["add_active"], "active")
        self.assertIsInstance(response.context["record_form"], RecordForm)
        self.assertIsInstance(response.context["water_form"], WaterForm)

    def test_post_for_valid_record_form_data(self) -> None:
        """Test post for valid record form data"""

        valid_record_form_data = {
            "purchase_datetime": timezone.now(),
            "item": "Test Item",
            "price": 123.45,
            "purchaser": self.user.pk,
            "record_submit": "",
        }

        # Send a POST request to the view
        response = self.client.post(
            self.url,
            data=valid_record_form_data,
        )

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/add_data.html")

        # Assert success message
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.SUCCESS)
        self.assertEqual(
            response_messages[0].message,
            "Your item record successfully added.",
        )

        # Assert context is correct
        self.assertEqual(response.context["add_active"], "active")
        self.assertIsInstance(response.context["record_form"], RecordForm)
        self.assertIsInstance(response.context["water_form"], WaterForm)

        # Assert that the record is saved in the database
        self.assertEqual(Record.objects.count(), 1)
        record: Type[Record] = Record.objects.first()  # type: ignore
        self.assertEqual(record.item, valid_record_form_data["item"])
        self.assertEqual(float(str(record.price)), valid_record_form_data["price"])
        self.assertEqual(record.purchaser, self.user)
        self.assertEqual(
            record.purchase_datetime, valid_record_form_data["purchase_datetime"]
        )
        self.assertEqual(record.adder, self.user)

    def test_post_for_invalid_record_form_data(self) -> None:
        """Test post for invalid record form data"""

        valid_record_form_data = {
            "item": "Test Item",
            "record_submit": "",
        }

        # Send a POST request to the view
        response = self.client.post(
            self.url,
            data=valid_record_form_data,
        )

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/add_data.html")

        # Assert error message
        response_messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.ERROR)
        self.assertEqual(response_messages[0].message, "Your item record not added.")

        # Assert context is correct
        self.assertEqual(response.context["add_active"], "active")
        self.assertIsInstance(response.context["record_form"], RecordForm)
        self.assertIsInstance(response.context["water_form"], WaterForm)

        # Assert that the record is not saved in the database
        self.assertEqual(Record.objects.count(), 0)

    def test_post_for_valid_water_form_data(self) -> None:
        """Test post for valid water form data"""

        valid_water_form_data = {
            "purchase_datetime": timezone.now(),
            "quantity": 1,
            "water_submit": "",
        }

        # Send a POST request to the view
        response = self.client.post(
            self.url,
            data=valid_water_form_data,
        )

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/add_data.html")

        # Assert success message
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.SUCCESS)
        self.assertEqual(
            response_messages[0].message,
            "Water record successfully added.",
        )

        # Assert context is correct
        self.assertEqual(response.context["add_active"], "active")
        self.assertIsInstance(response.context["record_form"], RecordForm)
        self.assertIsInstance(response.context["water_form"], WaterForm)

        # Assert that the water is saved in the database
        self.assertEqual(Water.objects.count(), 1)
        water: Type[Water] = Water.objects.first()  # type: ignore
        self.assertEqual(water.quantity, valid_water_form_data["quantity"])
        self.assertEqual(
            water.purchase_datetime, valid_water_form_data["purchase_datetime"]
        )
        self.assertEqual(water.adder, self.user)

    def test_post_for_invalid_water_form_data(self) -> None:
        """Test post for invalid water form data"""

        invalid_water_form_data = {
            "quantity": 1,
            "water_submit": "",
        }

        # Send a POST request to the view
        response = self.client.post(
            self.url,
            data=invalid_water_form_data,
        )

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/add_data.html")

        # Assert error message
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.ERROR)
        self.assertEqual(response_messages[0].message, "Water record not added.")

        # Assert context is correct
        self.assertEqual(response.context["add_active"], "active")
        self.assertIsInstance(response.context["record_form"], RecordForm)
        self.assertIsInstance(response.context["water_form"], WaterForm)

        # Assert that the water is not saved in the database
        self.assertEqual(Water.objects.count(), 0)

    def test_post_for_invalid_water_form_quantity_data(self) -> None:
        """Test post for invalid water form quantity data"""

        now = timezone.now()

        # Create water records with quantity 5
        Water.objects.create(
            quantity=5,
            adder=self.user,
            room=self.room,
            purchase_datetime=now,
        )

        invalid_water_form_data = {
            "purchase_datetime": now,
            "quantity": 1,
            "water_submit": "",
        }

        # Send a POST request to the view
        response = self.client.post(
            self.url,
            data=invalid_water_form_data,
        )

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/add_data.html")

        # Assert error message
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.WARNING)
        self.assertEqual(
            response_messages[0].message,
            "Maximum 5 water quantity allowed per day.",
        )

        # Assert context is correct
        self.assertEqual(response.context["add_active"], "active")
        self.assertIsInstance(response.context["record_form"], RecordForm)
        self.assertIsInstance(response.context["water_form"], WaterForm)

        # Assert that the water is not saved in the database
        self.assertEqual(Water.objects.count(), 1)

    def test_post_for_without_form_submit_info(self) -> None:
        """Test post for without form submit info"""

        # Send a POST request to the view
        response = self.client.post(
            self.url,
            data={},
        )

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/add_data.html")

        # Assert error message
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.ERROR)
        self.assertEqual(
            response_messages[0].message,
            "Please check and fill in all information correctly.",
        )

        # Assert context is correct
        self.assertEqual(response.context["add_active"], "active")
        self.assertIsInstance(response.context["record_form"], RecordForm)
        self.assertIsInstance(response.context["water_form"], WaterForm)


class TestRecordListView(TransactionTestCase):
    """Test record list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:records")
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

        self.room1 = Room.objects.create(name="test-room", admin=self.user1)
        self.room2 = Room.objects.create(name="test-room", admin=self.user2)

        # Create room 1 membership for user 2
        RoomMembership.objects.create(room=self.room1, member=self.user2)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room1.id
        session.save()

        # login user
        self.client.login(email="test@user1.com", password="test-password")

    def test_record_list_view_attributes(self) -> None:
        "Test record list view attributes"

        view = RecordListView()
        self.assertIsInstance(view, ListView)
        self.assertIsInstance(view, RoomRequiredMixin)
        self.assertEqual(view.model, Record)
        self.assertEqual(view.paginate_by, 20)
        self.assertEqual(view.paginate_orphans, 10)
        self.assertEqual(view.ordering, ["-purchase_datetime"])

    def test_record_list_view_working_for_room_records(self) -> None:
        """Test record list view working for room records"""

        # Create a record for user 1 room 1
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item 1",
            price=123.45,
            purchaser=self.user1,
            adder=self.user1,
            room=self.room1,
        )
        # Create a record for user 2 room 1
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item 2",
            price=123.45,
            purchaser=self.user1,
            adder=self.user2,
            room=self.room1,
        )

        # Create a record for room 2
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item 3",
            price=123.45,
            purchaser=self.user2,
            adder=self.user2,
            room=self.room2,
        )

        # Make a GET request to the view
        response = self.client.get(self.url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/record_list.html")

        # Assert context is correct
        self.assertTrue(response.context["room_records"], True)
        self.assertEqual(response.context["records_active"], "active")

        # Check that only room 1 records are present in the context
        self.assertQuerysetEqual(
            response.context["record_list"],
            Record.objects.filter(room=self.room1).order_by("-purchase_datetime"),
        )

    def test_record_list_view_working_for_search_room_records(self) -> None:
        """Test record list view working for search room records"""

        # Create records for room 1
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item 1",
            price=123.45,
            purchaser=self.user1,
            adder=self.user1,
            room=self.room1,
        )
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item Good",
            price=123.45,
            purchaser=self.user1,
            adder=self.user1,
            room=self.room1,
        )

        # Create a record for room 2
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item",
            price=123.45,
            purchaser=self.user2,
            adder=self.user2,
            room=self.room2,
        )

        search_item = "good"

        # Make a GET request to the view with search query
        response = self.client.get(self.url, {"query": search_item})

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/record_list.html")

        # Assert context is correct
        self.assertTrue(response.context["search_records"], search_item)
        self.assertEqual(response.context["records_active"], "active")

        # Check that only room 1 records contain item "good" are present in the context
        records = response.context["record_list"]
        self.assertQuerysetEqual(
            records,
            Record.objects.filter(room=self.room1, item="Test Item Good"),
        )

    def test_record_list_view_working_for_user_room_records(self) -> None:
        """Test record list view working for user room records"""

        # Create a record for user 1 room 1
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item 1",
            price=123.45,
            purchaser=self.user1,
            adder=self.user1,
            room=self.room1,
        )

        # Create a record for user 2 room  1
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item 2",
            price=123.45,
            purchaser=self.user2,
            adder=self.user2,
            room=self.room1,
        )

        # Create a record for user 2 room  2
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item 3",
            price=123.45,
            purchaser=self.user2,
            adder=self.user2,
            room=self.room1,
        )

        # Make a GET request to the view with user 1 pk
        member_records_url = reverse(
            "records:member_records",
            kwargs={"member_id": self.user1.pk},
        )
        response = self.client.get(member_records_url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/record_list.html")

        # Assert context is correct
        self.assertTrue(response.context["member_id"], self.user1.pk)

        # Check that only room 1 records with purchaser user 1 are present in the context
        self.assertQuerysetEqual(
            response.context["record_list"],
            Record.objects.filter(room=self.room1, purchaser=self.user1),
        )

    def test_record_list_view_working_for_search_user_room_records(self) -> None:
        """Test record list view working for search user room records"""

        # Create records for room 1
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item 1",
            price=123.45,
            purchaser=self.user1,
            adder=self.user1,
            room=self.room1,
        )
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item Good 2",
            price=123.45,
            purchaser=self.user1,
            adder=self.user1,
            room=self.room1,
        )

        # Create records for room 2
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item 3",
            price=123.45,
            purchaser=self.user2,
            adder=self.user2,
            room=self.room2,
        )
        Record.objects.create(
            purchase_datetime=timezone.now(),
            item="Test Item Good 4",
            price=123.45,
            purchaser=self.user2,
            adder=self.user2,
            room=self.room2,
        )

        search_item = "good"

        # Make a GET request to the view with user 1 pk and search query
        member_records_url = reverse(
            "records:member_records",
            kwargs={"member_id": self.user1.pk},
        )
        response = self.client.get(member_records_url, {"query": search_item})

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/record_list.html")

        # Assert context is correct
        self.assertTrue(response.context["member_id"], self.user1.pk)

        # Check that only room1 records with purchaser user 1
        # contain item "good" are present in the context
        records = response.context["record_list"]
        self.assertQuerysetEqual(
            records,
            Record.objects.filter(
                room=self.room1,
                purchaser=self.user1,
                item="Test Item Good 2",
            ),
        )


class TestWaterListView(TransactionTestCase):
    """Test water list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:waters")
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

        self.room1 = Room.objects.create(name="test-room", admin=self.user1)
        self.room2 = Room.objects.create(name="test-room", admin=self.user2)

        # Create room 1 membership for user 2
        RoomMembership.objects.create(room=self.room1, member=self.user2)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room1.id
        session.save()

        # login user
        self.client.login(email="test@user1.com", password="test-password")

    def test_water_list_view_attributes(self) -> None:
        "Test water list view attributes"

        view = WaterListView()
        self.assertIsInstance(view, ListView)
        self.assertIsInstance(view, RoomRequiredMixin)
        self.assertEqual(view.model, Water)
        self.assertEqual(view.paginate_by, 20)
        self.assertEqual(view.paginate_orphans, 10)
        self.assertEqual(view.ordering, ["-purchase_datetime"])

    def test_water_list_view_working(self) -> None:
        """Test water list view working"""

        # Create water records for user 1 room 1
        Water.objects.create(
            purchase_datetime=timezone.now(),
            quantity=1,
            room=self.room1,
            adder=self.user1,
        )
        Water.objects.create(
            purchase_datetime=timezone.now(),
            quantity=1,
            room=self.room1,
            adder=self.user2,
        )

        # Create a water record for user 2 room 2
        Water.objects.create(
            purchase_datetime=timezone.now(),
            quantity=1,
            room=self.room2,
            adder=self.user2,
        )

        # Make a GET request to the view
        response = self.client.get(self.url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "records/water_list.html")

        # Assert context is correct
        self.assertEqual(response.context["waters_active"], "active")

        # Check that the water records are present in the context
        self.assertQuerysetEqual(
            response.context["water_list"],
            Water.objects.filter(room=self.room1).order_by("-purchase_datetime"),
        )


class TestExportDataView(TestCase):
    """Test export data view"""

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )
        self.url = reverse("records:export_data")
        self.room = Room.objects.create(name="test-room", admin=self.user)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # login user
        self.client.login(email="test@user.com", password="test-password")

    def test_export_data_view_attributes(self) -> None:
        """Test export data view attributes"""

        view = ExportDataView()
        self.assertIsInstance(view, ListView)
        self.assertIsInstance(view, RoomRequiredMixin)
        self.assertEqual(view.model, User)
        self.assertEqual(view.ordering, ["-id"])
        self.assertEqual(view.paginate_by, 20)
        self.assertEqual(view.paginate_orphans, 10)
        self.assertEqual(view.context_object_name, "room_member_list")
        self.assertEqual(view.template_name, "records/export_data.html")

    def test_export_data_view_working(self) -> None:
        """Test export data view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/export_data.html")

        # Assert context is correct
        self.assertEqual(response.context["export_data_active"], "active")
        self.assertQuerysetEqual(
            response.context["room_member_list"],
            User.objects.filter(room_membership__room=self.room),
        )


class TestRoomReportView(TestCase):
    """Test room report view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("records:room_reports")

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
        self.user3 = User.objects.create_user(
            email="test@user3.com",
            password="test-password",
            first_name="test",
            last_name="user2",
        )

        # Create room
        self.room = Room.objects.create(name="test-room", admin=self.user1)
        RoomMembership.objects.create(room=self.room, member=self.user2)
        RoomMembership.objects.create(room=self.room, member=self.user3)

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # login user
        self.client.login(email="test@user1.com", password="test-password")

    def test_room_report_view_attributes(self) -> None:
        """Test room report view attributes"""

        view = RoomReportView()
        self.assertIsInstance(view, View)
        self.assertIsInstance(view, RoomRequiredMixin)

    def test_room_report_view_working(self) -> None:
        """Test room report view working"""

        # Create some test records
        Record.objects.create(
            purchase_datetime=timezone.now(),
            purchaser=self.user1,
            adder=self.user1,
            price=120,
            room=self.room,
        )
        Record.objects.create(
            purchase_datetime=timezone.now(),
            purchaser=self.user1,
            adder=self.user1,
            price=80,
            room=self.room,
        )
        Record.objects.create(
            purchase_datetime=timezone.now(),
            purchaser=self.user2,
            adder=self.user2,
            price=100,
            room=self.room,
        )

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the expected context variables are present in the response
        self.assertEqual(response.context["room_reports_active"], "active")
        self.assertEqual(response.context["room_records_count"], 3)
        self.assertEqual(response.context["room_total_price"], 300)
        self.assertEqual(response.context["per_member_price"], 100)

        room_members_report = response.context["room_members_report"]
        self.assertEqual(len(room_members_report), 3)

        # Assertion for user 1
        self.assertEqual(room_members_report[0]["room_member"], self.user1)
        self.assertEqual(room_members_report[0]["total_spent"], 200)
        self.assertEqual(room_members_report[0]["price_diff"], -100)
        self.assertEqual(room_members_report[0]["records_count"], 2)

        # Assertion for user 2
        self.assertEqual(room_members_report[1]["room_member"], self.user2)
        self.assertEqual(room_members_report[1]["total_spent"], 100)
        self.assertEqual(room_members_report[1]["price_diff"], 0)
        self.assertEqual(room_members_report[1]["records_count"], 1)

        # Assertion for user 3
        self.assertEqual(room_members_report[2]["room_member"], self.user3)
        self.assertEqual(room_members_report[2]["total_spent"], 0)
        self.assertEqual(room_members_report[2]["price_diff"], 100)
        self.assertEqual(room_members_report[2]["records_count"], 0)

    def test_room_report_view_working_for_zero_state(self) -> None:
        """Test room report view working for zero state"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the expected context variables are present in the response
        self.assertEqual(response.context["room_reports_active"], "active")
        self.assertEqual(response.context["room_records_count"], 0)
        self.assertEqual(response.context["room_total_price"], 0)
        self.assertEqual(response.context["per_member_price"], 0)

        room_members_report = response.context["room_members_report"]
        self.assertEqual(len(room_members_report), 3)

        # Assertion for user 1
        self.assertEqual(room_members_report[0]["room_member"], self.user1)
        self.assertEqual(room_members_report[0]["total_spent"], 0)
        self.assertEqual(room_members_report[0]["price_diff"], 0)
        self.assertEqual(room_members_report[0]["records_count"], 0)

        # Assertion for user 2
        self.assertEqual(room_members_report[1]["room_member"], self.user2)
        self.assertEqual(room_members_report[1]["total_spent"], 0)
        self.assertEqual(room_members_report[1]["price_diff"], 0)
        self.assertEqual(room_members_report[1]["records_count"], 0)

        # Assertion for user 3
        self.assertEqual(room_members_report[2]["room_member"], self.user3)
        self.assertEqual(room_members_report[2]["total_spent"], 0)
        self.assertEqual(room_members_report[2]["price_diff"], 0)
        self.assertEqual(room_members_report[2]["records_count"], 0)


class TestBaseExportView(TestCase):
    """Test base export view"""

    def setUp(self) -> None:
        self.export_view = BaseExportView()

    def test_base_export_view_attributes(self) -> None:
        "Test base export view attributes"

        self.assertIsInstance(self.export_view, RoomRequiredMixin)
        self.assertIsInstance(self.export_view, View)

    @mock.patch.object(pd.DataFrame, "to_excel")
    def test_write_to_sheet_working(self, mock_to_excel) -> None:
        """Test write to sheet working"""

        # Create a mock Excel writer
        mock_writer = mock.MagicMock()

        sheet_name = "test-sheet"

        # Create a sample DataFrame
        data = pd.DataFrame({"Column1": [1, 2], "Column2": ["A", "B"]})

        # Call the write_to_sheet method
        self.export_view.write_to_sheet(mock_writer, sheet_name, data)

        # Check that to_excel was called once with the correct arguments
        mock_to_excel.assert_called_once_with(
            mock_writer, sheet_name=sheet_name, index=False
        )

    @mock.patch("records.views.RoomExporter")
    @mock.patch.object(BaseExportView, "get_room")
    def test_get_room_and_export_instance(
        self, mock_get_room, mock_room_exporter
    ) -> None:
        """Test get room and export instance working"""

        # Create a mock request object
        mock_request = mock.MagicMock()

        # Create a mock Room object
        mock_room = mock.MagicMock(spec=Room)
        mock_room.id = 123

        # Create a mock RoomExporter object
        mock_exporter = mock.MagicMock(spec=RoomExporter)

        # Set up the mocks
        mock_get_room.return_value = mock_room
        mock_room_exporter.return_value = mock_exporter

        # Set base export view instance request object
        self.export_view.request = mock_request

        # Call the method to test
        room, exporter = self.export_view.get_room_and_export_instance()

        # Check that get_room was called with the correct arguments
        mock_get_room.assert_called_once_with(mock_request)

        # Check that RoomExporter was initialized with the correct room ID
        mock_room_exporter.assert_called_once_with(mock_room.id)

        # Check the return values are correct
        self.assertEqual(room, mock_room)
        self.assertEqual(exporter, mock_exporter)

    @mock.patch("pandas.ExcelWriter")
    @mock.patch.object(BaseExportView, "write_to_sheet")
    def test_generate_excel_buffer_working(
        self, mock_write_to_sheet, mock_excel_writer
    ) -> None:
        """Test generate excel buffer working"""

        # Mock the ExcelWriter
        mock_writer = mock.MagicMock()
        mock_excel_writer.return_value.__enter__.return_value = mock_writer

        # Sample data to pass into the function
        data = [
            ("Sheet1", pd.DataFrame({"A": [1, 2], "B": [3, 4]})),
            ("Sheet2", pd.DataFrame({"X": [5, 6], "Y": [7, 8]})),
        ]

        # Call the method to test
        buffer = self.export_view.generate_excel_buffer(data)

        # Ensure ExcelWriter was called with the correct buffer and engine
        mock_excel_writer.assert_called_once_with(buffer, engine="xlsxwriter")

        # Check that write_to_sheet was called for each sheet with correct arguments
        self.assertEqual(mock_write_to_sheet.call_count, len(data))

        # Verify that write_to_sheet was called with the correct arguments for each sheet
        for i, (sheet_name, df) in enumerate(data):
            mock_write_to_sheet.assert_any_call(mock_writer, sheet_name, df)

        # Ensure the buffer is a BytesIO instance
        self.assertIsInstance(buffer, BytesIO)

        # Check if the buffer's seek position is at 0
        self.assertEqual(buffer.tell(), 0)

    def test_generate_excel_response_working(self) -> None:
        """Test generate excel response working"""

        # Create a mock io.BytesIO buffer to simulate an Excel file
        mock_buffer = mock.MagicMock(spec=BytesIO)
        mocked_excel_data = b"mocked-excel-data"
        mock_buffer.getvalue.return_value = mocked_excel_data

        # Define the file name
        file_name = "test-excel-file"

        # Call the method to test
        response = self.export_view.generate_excel_response(file_name, mock_buffer)

        # Check that HttpResponse is returned
        self.assertIsInstance(response, HttpResponse)

        # Verify that the response content type is correct
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Verify that the Content-Disposition header is set correctly for attachment
        self.assertEqual(
            response["Content-Disposition"],
            f"attachment; filename={file_name}.xlsx",
        )

        # Check that the response content is set to the value returned by the buffer
        self.assertEqual(response.content, mocked_excel_data)

        # Check that the buffer's getvalue method was called
        mock_buffer.getvalue.assert_called_once()

    @mock.patch.object(BaseExportView, "generate_excel_buffer")
    @mock.patch.object(BaseExportView, "generate_excel_response")
    def test_get_file_response(
        self, mock_generate_excel_response, mock_generate_excel_buffer
    ) -> None:
        """Test get file response working"""

        # Prepare test data: list of tuples (sheet_name, DataFrame)
        data = [
            ("Sheet1", pd.DataFrame({"A": [1, 2], "B": [3, 4]})),
            ("Sheet2", pd.DataFrame({"X": [5, 6], "Y": [7, 8]})),
        ]
        file_name = "test-excel-file"

        # Create mock buffer for generate_excel_buffer
        mock_buffer = mock.MagicMock(spec=BytesIO)

        # Create mock HttpResponse for generate_excel_response
        mock_response = mock.MagicMock(spec=HttpResponse)

        # Mock the return values of the methods
        mock_generate_excel_buffer.return_value = mock_buffer
        mock_generate_excel_response.return_value = mock_response

        # Call the method
        response = self.export_view.get_file_response(file_name, data)

        # Verify that generate_excel_buffer was called with the correct data
        mock_generate_excel_buffer.assert_called_once_with(data)

        # Verify that generate_excel_response was called with the correct file_name and buffer
        mock_generate_excel_response.assert_called_once_with(file_name, mock_buffer)

        # Check that the returned response is the mock response
        self.assertEqual(response, mock_response)


# TODO: Update it
# class TestOverallXlsView(TestCase):
#     """Test overall xls view"""

#     def setUp(self) -> None:
#         self.client = Client()
#         self.url = reverse("records:overall_xls")

#     @mock.patch("records.views.get_excel")
#     def test_overall_xls_view_working(self, mock_get_excel) -> None:
#         """Test overall xls view working"""

#         # Send a GET request to the view
#         response = self.client.get(self.url)

#         # Assert that get_excel function is called once
#         mock_get_excel.assert_called_once()

#         # Assert that the response status code is 200 (OK)
#         self.assertEqual(response.status_code, HTTPStatus.OK)

#         # Assert that the content type of the response is application/ms-excel
#         self.assertEqual(response["Content-Type"], "application/ms-excel")

#         # Assert that the content disposition is correctly set
#         expected_filename = "Overall Items Records.xls"
#         self.assertEqual(
#             response["Content-Disposition"],
#             f"attachment; filename={expected_filename}",
#         )

# TODO: Update it
# class TestUserXlsView(TestCase):
#     """Test user xls view"""

#     def setUp(self) -> None:
#         self.client = Client()
#         self.user = User.objects.create_user(
#             email="test@user.com",
#             password="test-password",
#             first_name="test",
#             last_name="user",
#         )
#         self.url = reverse("records:user_xls", kwargs={"user_id": self.user.pk})

#     @mock.patch("records.views.get_excel")
#     def test_user_xls_view_working(self, mock_get_excel) -> None:
#         """Test user xls view working"""

#         # Send a GET request to the view
#         response = self.client.get(self.url)

#         # Assert that get_excel function is called once
#         mock_get_excel.assert_called_once()

#         # Assert that the response status code is 200 (OK)
#         self.assertEqual(response.status_code, HTTPStatus.OK)

#         # Assert that the content type of the response is application/ms-excel
#         self.assertEqual(response["Content-Type"], "application/ms-excel")

#         # Assert that the content disposition is correctly set
#         expected_filename = f"{self.user.get_full_name()} Items Records.xls"
#         self.assertEqual(
#             response["Content-Disposition"],
#             f"attachment; filename={expected_filename}",
#         )


# TODO: Update it
# class TestWaterXlsView(TestCase):
#     """Test water xls view"""

#     def setUp(self) -> None:
#         self.client = Client()
#         self.url = reverse("records:water_xls")

#     @mock.patch("records.views.get_excel")
#     def test_water_xls_view_working(self, mock_get_excel) -> None:
#         """Test water xls view working"""

#         # Send a GET request to the view
#         response = self.client.get(self.url)

#         # Assert that get_excel function is called once
#         mock_get_excel.assert_called_once()

#         # Assert that the response status code is 200 (OK)
#         self.assertEqual(response.status_code, HTTPStatus.OK)

#         # Assert that the content type of the response is application/ms-excel
#         self.assertEqual(response["Content-Type"], "application/ms-excel")

#         # Assert that the content disposition is correctly set
#         expected_filename = "Water Entry Records.xls"
#         self.assertEqual(
#             response["Content-Disposition"],
#             f"attachment; filename={expected_filename}",
#         )


# TODO: Update it
# class TestMaidXlsView(TestCase):
#     """Test maid xls view"""

#     def setUp(self) -> None:
#         self.client = Client()
#         self.url = reverse("records:maid_xls")

#     @mock.patch("records.views.get_excel")
#     def test_maid_xls_view_working(self, mock_get_excel) -> None:
#         """Test maid xls view working"""

#         # Send a GET request to the view
#         response = self.client.get(self.url)

#         # Assert that get_excel function is called once
#         mock_get_excel.assert_called_once()

#         # Assert that the response status code is 200 (OK)
#         self.assertEqual(response.status_code, HTTPStatus.OK)

#         # Assert that the content type of the response is application/ms-excel
#         self.assertEqual(response["Content-Type"], "application/ms-excel")

#         # Assert that the content disposition is correctly set
#         expected_filename = "Maid Salary Records.xls"
#         self.assertEqual(
#             response["Content-Disposition"],
#             f"attachment; filename={expected_filename}",
#         )


# TODO: Update it
# class TestElectricityXlsView(TestCase):
#     """Test electricity xls view"""

#     def setUp(self) -> None:
#         self.client = Client()
#         self.url = reverse("records:electricity_xls")

#     @mock.patch("records.views.get_excel")
#     def test_electricity_xls_view_working(self, mock_get_excel) -> None:
#         """Test electricity xls view working"""

#         # Send a GET request to the view
#         response = self.client.get(self.url)

#         # Assert that get_excel function is called once
#         mock_get_excel.assert_called_once()

#         # Assert that the response status code is 200 (OK)
#         self.assertEqual(response.status_code, HTTPStatus.OK)

#         # Assert that the content type of the response is application/ms-excel
#         self.assertEqual(response["Content-Type"], "application/ms-excel")

#         # Assert that the content disposition is correctly set
#         expected_filename = "Electricity Bill Records.xls"
#         self.assertEqual(
#             response["Content-Disposition"],
#             f"attachment; filename={expected_filename}",
#         )
