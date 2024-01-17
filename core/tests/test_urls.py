from django.test import TestCase
from django.urls import resolve, reverse

from core import views


class TestUrls(TestCase):
    """Test url patterns"""

    def test_home_url(self):
        """Test home url resolve"""

        url = reverse("core:home")
        self.assertEqual(resolve(url).func, views.home)

    def test_about_url(self):
        """Test about url resolve"""

        url = reverse("core:about")
        self.assertEqual(resolve(url).func.view_class, views.AboutTemplateView)

    def test_feedback_url(self):
        """Test feedback url resolve"""

        url = reverse("core:feedback")
        self.assertEqual(resolve(url).func.view_class, views.FeedbackCreateView)
