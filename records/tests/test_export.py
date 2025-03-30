from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import localtime, make_aware

from accounts.models import RoomMembership
from records.export import RoomExporter
from records.models import Electricity, Maid, Record, Room, Water

User = get_user_model()


class RoomExporterTest(TestCase):
    """Unit tests for RoomExporter class"""

    def setUp(self):
        self.room_id = 1
        self.mock_df = pd.DataFrame([{"Mock": "Data"}])
        self.exporter = RoomExporter(room_id=self.room_id)

        self.admin = User.objects.create_user(
            email="admin@user.com",
            password="test-password",
            first_name="admin",
            last_name="user",
        )

        self.member = User.objects.create_user(
            email="member@user.com",
            password="test-password",
            first_name="member",
            last_name="user",
        )

        self.room = Room.objects.create(name="test-room", admin=self.admin)
        RoomMembership.objects.create(room=self.room, member=self.member)

    def test_attribute(self):
        """Test attribute"""

        self.assertEqual(self.exporter.room_id, self.room_id)

    def test_get_formatted_date(self):
        """Test get formatted date"""

        test_date = make_aware(datetime(2025, 2, 18, 14, 30))
        formatted_date = self.exporter.get_formatted_date(test_date)
        self.assertEqual(formatted_date, "18-02-2025")

    def test_get_formatted_time(self):
        """Test get formatted time"""

        test_time = make_aware(datetime(2025, 2, 18, 14, 30))
        formatted_time = self.exporter.get_formatted_time(test_time)
        self.assertEqual(formatted_time, "02:30:00 PM")

    @patch("records.export.RoomExporter.get_entry_df")
    def test_get_maid_df(self, mock_get_entry_df: MagicMock):
        """Mock test for get maid df"""

        # Prepare mock DataFrame
        mock_get_entry_df.return_value = self.mock_df

        # Call the method you're testing
        df = self.exporter.get_maid_df()

        # Assert that get_entry_df was called with Maid as an argument
        mock_get_entry_df.assert_called_with(Maid)

        # Assert the DataFrame returned is as expected
        self.assertTrue(df.equals(self.mock_df))

    @patch("records.export.RoomExporter.get_entry_df")
    def test_get_electricity_df(self, mock_get_entry_df: MagicMock):
        """Mock test for get electricity df"""

        # Prepare mock DataFrame
        mock_get_entry_df.return_value = self.mock_df

        # Call the method you're testing
        df = self.exporter.get_electricity_df()

        # Assert that get_entry_df was called with Electricity as an argument
        mock_get_entry_df.assert_called_with(Electricity)

        # Assert the DataFrame returned is as expected
        self.assertTrue(df.equals(self.mock_df))

    def test_get_entry_df(self):
        """Test get entry df"""

        price1 = 1234
        price2 = 5678

        current_datetime = timezone.now()
        due_datetime1 = current_datetime
        due_datetime2 = current_datetime - timedelta(days=1)

        formatted_current_date = localtime(current_datetime).strftime("%d-%m-%Y")
        formatted_due_date1 = localtime(due_datetime1).strftime("%d-%m-%Y")
        formatted_due_date2 = localtime(due_datetime2).strftime("%d-%m-%Y")

        formatted_current_time = localtime(current_datetime).strftime("%I:%M:%S %p")
        formatted_due_time1 = localtime(due_datetime1).strftime("%I:%M:%S %p")
        formatted_due_time2 = localtime(due_datetime2).strftime("%I:%M:%S %p")

        Electricity.objects.create(
            price=price1,
            due_datetime=due_datetime1,
        )

        Electricity.objects.create(
            price=price2,
            due_datetime=due_datetime2,
        )

        df = self.exporter.get_entry_df(Electricity)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["Date"], formatted_due_date2)
        self.assertEqual(df.iloc[0]["Time"], formatted_due_time2)
        self.assertEqual(df.iloc[0]["Price"], price2)
        self.assertEqual(df.iloc[0]["Entry ID"], 2)
        self.assertEqual(df.iloc[0]["Entry Date"], formatted_current_date)
        self.assertEqual(df.iloc[0]["Entry Time"], formatted_current_time)
        self.assertEqual(df.iloc[0]["Last Modified Date"], formatted_current_date)
        self.assertEqual(df.iloc[0]["Last Modified Time"], formatted_current_time)
        self.assertEqual(df.iloc[1]["Date"], formatted_due_date1)
        self.assertEqual(df.iloc[1]["Time"], formatted_due_time1)
        self.assertEqual(df.iloc[1]["Price"], price1)
        self.assertEqual(df.iloc[1]["Entry ID"], 1)
        self.assertEqual(df.iloc[1]["Entry Date"], formatted_current_date)
        self.assertEqual(df.iloc[1]["Entry Time"], formatted_current_time)
        self.assertEqual(df.iloc[1]["Last Modified Date"], formatted_current_date)
        self.assertEqual(df.iloc[1]["Last Modified Time"], formatted_current_time)

    def test_get_water_df(self):
        """Test get water df"""

        quantity1 = 1
        quantity2 = 2

        current_datetime = timezone.now()
        purchase_datetime1 = current_datetime
        purchase_datetime2 = current_datetime - timedelta(days=1)

        formatted_current_date = localtime(current_datetime).strftime("%d-%m-%Y")
        formatted_purchase_date1 = localtime(purchase_datetime1).strftime("%d-%m-%Y")
        formatted_purchase_date2 = localtime(purchase_datetime2).strftime("%d-%m-%Y")

        formatted_current_time = localtime(current_datetime).strftime("%I:%M:%S %p")
        formatted_purchase_time1 = localtime(purchase_datetime1).strftime("%I:%M:%S %p")
        formatted_purchase_time2 = localtime(purchase_datetime2).strftime("%I:%M:%S %p")

        Water.objects.create(
            quantity=quantity1,
            adder=self.admin,
            room=self.room,
            purchase_datetime=purchase_datetime1,
        )

        Water.objects.create(
            quantity=quantity2,
            adder=self.member,
            room=self.room,
            purchase_datetime=purchase_datetime2,
        )

        df = self.exporter.get_water_df()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["Date"], formatted_purchase_date2)
        self.assertEqual(df.iloc[0]["Time"], formatted_purchase_time2)
        self.assertEqual(df.iloc[0]["Quantity"], quantity2)
        self.assertEqual(df.iloc[0]["Entry ID"], 2)
        self.assertEqual(df.iloc[0]["Entry Date"], formatted_current_date)
        self.assertEqual(df.iloc[0]["Entry Time"], formatted_current_time)
        self.assertEqual(df.iloc[0]["Last Modified Date"], formatted_current_date)
        self.assertEqual(df.iloc[0]["Last Modified Time"], formatted_current_time)
        self.assertEqual(df.iloc[1]["Date"], formatted_purchase_date1)
        self.assertEqual(df.iloc[1]["Time"], formatted_purchase_time1)
        self.assertEqual(df.iloc[1]["Quantity"], quantity1)
        self.assertEqual(df.iloc[1]["Entry ID"], 1)
        self.assertEqual(df.iloc[1]["Entry Date"], formatted_current_date)
        self.assertEqual(df.iloc[1]["Entry Time"], formatted_current_time)
        self.assertEqual(df.iloc[1]["Last Modified Date"], formatted_current_date)
        self.assertEqual(df.iloc[1]["Last Modified Time"], formatted_current_time)
