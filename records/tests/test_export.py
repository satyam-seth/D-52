from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from records.export import RoomExporter


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
