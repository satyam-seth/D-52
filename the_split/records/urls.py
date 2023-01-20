from django.urls import path
from records import views

app_name = "records"

urlpatterns = [
    path("add/", views.AddTemplateView.as_view(), name="add"),
    path("item/", views.RecordAddView.as_view(), name="add_item"),
    path("water/", views.WaterAddView.as_view(), name="add_water"),
    path("records/", views.RecordListView.as_view(), name="records"),
    path(
        "detailed/<int:user_id>/", views.UserRecordListView.as_view(), name="detailed"
    ),
    path("detailed_water/", views.WaterListView.as_view(), name="detailed_water"),
    path("search/", views.SearchListView.as_view(), name="search"),
    path("download/", views.DownloadTemplateView.as_view(), name="download"),
    path("report/", views.report, name="report"),
    path("overall_xls/", views.overall_xls, name="overall_xls"),
    path("<str:user>/", views.user_xls, name="user_xls"),
    # path('water_xls/',views.water_xls,name='water_xls'),
]
