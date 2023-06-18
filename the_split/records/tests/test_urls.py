from django.test import TestCase
from django.urls import resolve, reverse
from records import views


class TestUrls(TestCase):
    """Test url patterns"""

    def test_add_url(self):
        """Test add url resolve"""

        url = reverse("records:add")
        self.assertEqual(resolve(url).func.view_class, views.AddTemplateView)

    def test_add_item_url(self):
        """Test add item url resolve"""

        url = reverse("records:add_item")
        self.assertEqual(resolve(url).func.view_class, views.RecordAddView)

    def test_add_water_url(self):
        """Test add water url resolve"""

        url = reverse("records:add_water")
        self.assertEqual(resolve(url).func.view_class, views.WaterAddView)

    def test_records_url(self):
        """Test records url resolve"""

        url = reverse("records:records")
        self.assertEqual(resolve(url).func.view_class, views.RecordListView)

    def test_detailed_url(self):
        """Test detailed url resolve"""

        url = reverse("records:detailed", args=[1])  # Assuming user_id is 1
        self.assertEqual(resolve(url).func.view_class, views.UserRecordListView)

    def test_detailed_water_url(self):
        """Test detailed water url resolve"""

        url = reverse("records:detailed_water")
        self.assertEqual(resolve(url).func.view_class, views.WaterListView)

    def test_search_url(self):
        """Test search url resolve"""

        url = reverse("records:search")
        self.assertEqual(resolve(url).func.view_class, views.SearchListView)

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

    # def test_water_xls_url(self):
    #     """Test water xls url resolve"""

    #     url = reverse("records:water_xls")
    #     self.assertEqual(resolve(url).func, views.water_xls)
