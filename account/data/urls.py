from django.urls import path

from data import views

# TODO: add namespace  'app = "data"'

urlpatterns = [
    path("add/", views.add, name="add"),
    path("item/", views.add_item, name="add_item"),
    path("water/", views.add_water, name="add_water"),
    path("records/", views.RecordListView.as_view(), name="records"),
    path("detailed/<int:user_id>/", views.detailed_view, name="detailed"),
    path("detailed_water/", views.detailed_water_view, name="detailed_water"),
    path("report/", views.report, name="report"),
    path("search/", views.search, name="search"),
    path("download/", views.download, name="download"),
    path("overall_xls/", views.overall_xls, name="overall_xls"),
    path("<str:user>/", views.user_xls, name="user_xls"),
    # path('water_xls/',views.water_xls,name='water_xls'),
]
