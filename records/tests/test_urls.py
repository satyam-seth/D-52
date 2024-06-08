from django.test import TestCase
from django.urls import resolve, reverse

from records import views


class TestUrls(TestCase):
    """Test url patterns"""

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

    def test_water_url(self):
        """Test water url resolve"""

        url = reverse("records:water")
        self.assertEqual(resolve(url).func.view_class, views.WaterListView)

    def test_download_url(self):
        """Test download url resolve"""

        url = reverse("records:download")
        self.assertEqual(resolve(url).func.view_class, views.DownloadTemplateView)

    def test_report_url(self):
        """Test report url resolve"""

        url = reverse("records:report")
        self.assertEqual(resolve(url).func, views.report)

    def test_overall_xls_url(self):
        """Test overall xls url resolve"""

        url = reverse("records:overall_xls")
        self.assertEqual(resolve(url).func, views.overall_xls)

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
