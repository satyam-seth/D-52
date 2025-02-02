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

    def test_user_records_url(self):
        """Test user records url resolve"""

        url = reverse("records:user_records", args=[1])  # Assuming user_id is 1
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

    def test_user_xls_url(self):
        """Test user xls url resolve"""

        url = reverse("records:user_xls", args=[1])  # Assuming username is provided
        self.assertEqual(resolve(url).func, views.user_xls)

    def test_water_xls_url(self):
        """Test water xls url resolve"""

        url = reverse("records:water_xls")
        self.assertEqual(resolve(url).func, views.water_xls)

    def test_electricity_xls_url(self):
        """Test electricity xls url resolve"""

        url = reverse("records:electricity_xls")
        self.assertEqual(resolve(url).func, views.electricity_xls)

    def test_maid_xls_url(self):
        """Test maid xls url resolve"""

        url = reverse("records:maid_xls")
        self.assertEqual(resolve(url).func, views.maid_xls)
