from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
from django.test import TestCase
from django.utils.timezone import make_aware

from records.export import RoomExporter
from records.models import Electricity


class RoomExporterTest(TestCase):
    """Unit tests for RoomExporter class"""

    def setUp(self):
        self.room_id = 1
        self.exporter = RoomExporter(room_id=self.room_id)

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
    def test_get_electricity_df(self, mock_get_entry_df: MagicMock):
        """Mock test for get electricity df"""

        # Prepare mock DataFrame
        mock_df = pd.DataFrame([{"Mock": "Data"}])
        mock_get_entry_df.return_value = mock_df

        # Call the method you're testing
        df = self.exporter.get_electricity_df()

        # Assert that get_entry_df was called with Electricity as an argument
        mock_get_entry_df.assert_called_with(Electricity)

        # Assert the DataFrame returned is as expected
        self.assertTrue(df.equals(mock_df))
