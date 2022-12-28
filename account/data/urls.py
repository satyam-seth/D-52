from django.urls import path
from data import views

urlpatterns = [
    path("add/", views.add, name="add"),
    path("item/", views.add_item, name="add_item"),
    path("water/", views.add_water, name="add_water"),
    path("records/", views.records, name="records"),
    path("detailed/<str:var>/", views.detailed_view, name="detailed"),
    path("report/", views.report, name="report"),
    path("download/", views.download, name="download"),
    path("overall_xls/", views.overall_xls, name="overall_xls"),
    path("<str:user>/", views.user_xls, name="user_xls"),
    # path('water_xls/',views.water_xls,name='water_xls'),
]
