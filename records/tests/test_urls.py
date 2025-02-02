from django.test import TestCase
from django.urls import resolve, reverse

from records import views


class TestUrls(TestCase):
    """Test url patterns"""

    def test_dashboard_url(self):
        """Test dashboard url resolve"""

        url = reverse("records:dashboard")
        self.assertEqual(resolve(url).func.view_class, views.DashboardTemplateView)

    def test_add_data_url(self):
        """Test add data url resolve"""

        url = reverse("records:add_data")
        self.assertEqual(resolve(url).func.view_class, views.AddDataView)

    def test_records_url(self):
        """Test records url resolve"""

        url = reverse("records:records")
        self.assertEqual(resolve(url).func.view_class, views.RecordListView)

    def test_member_records_url(self):
        """Test member records url resolve"""

        url = reverse("records:member_records", args=[1])  # Assuming user_id is 1
        self.assertEqual(resolve(url).func.view_class, views.RecordListView)

    def test_waters_url(self):
        """Test waters url resolve"""

        url = reverse("records:waters")
        self.assertEqual(resolve(url).func.view_class, views.WaterListView)

    def test_export_data_url(self):
        """Test export data url resolve"""

        url = reverse("records:export_data")
        self.assertEqual(resolve(url).func.view_class, views.ExportDataView)

    def test_room_reports_url(self):
        """Test room reports url resolve"""

        url = reverse("records:room_reports")
        self.assertEqual(resolve(url).func.view_class, views.RoomReportView)

    def test_export_all_records_url(self):
        """Test export all records url resolve"""

        url = reverse("records:export_all_records")
        self.assertEqual(resolve(url).func.view_class, views.ExportAllRecordView)

    def test_export_member_records_url(self):
        """Test export member records url resolve"""

        url = reverse(
            "records:export_member_records",
            args=[1],  # Assuming username is provided
        )
        self.assertEqual(resolve(url).func.view_class, views.ExportMemberRecordView)

    def test_export_water_url(self):
        """Test export water url resolve"""

        url = reverse("records:export_water")
        self.assertEqual(resolve(url).func.view_class, views.ExportWaterView)

    def test_export_maid_url(self):
        """Test export maid url resolve"""

        url = reverse("records:export_maid")
        self.assertEqual(resolve(url).func.view_class, views.ExportMaidView)

    def test_export_electricity_url(self):
        """Test export electricity url resolve"""

        url = reverse("records:export_electricity")
        self.assertEqual(resolve(url).func.view_class, views.ExportElectricityView)
