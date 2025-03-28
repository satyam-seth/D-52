from django.test import TestCase

from records.export import RoomExporter


class RoomExporterTest(TestCase):
    """Unit tests for RoomExporter class"""

    def setUp(self):
        """Set up test data."""
        self.room_id = 1

        self.exporter = RoomExporter(room_id=self.room_id)

    def test_attribute(self):
        """Test attribute"""

        self.assertEqual(self.exporter.room_id, self.room_id)
