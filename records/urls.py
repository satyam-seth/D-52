from django.urls import path

from records import views

app_name = "records"

urlpatterns = [
    path("add_data/", views.AddDataView.as_view(), name="add_data"),
    path("records/", views.RecordListView.as_view(), name="records"),
    path("records/<int:user_id>/", views.RecordListView.as_view(), name="user_records"),
    path("waters/", views.WaterListView.as_view(), name="waters"),
    path("export_data/", views.ExportDataView.as_view(), name="export_data"),
    path("room_reports/", views.RoomReportView.as_view(), name="room_reports"),
    path("download/overall/", views.overall_xls, name="overall_xls"),
    path("download/<int:user_id>/", views.user_xls, name="user_xls"),
    path("water_xls/", views.water_xls, name="water_xls"),
    path("electricity_xls/", views.electricity_xls, name="electricity_xls"),
    path("maid_xls/", views.maid_xls, name="maid_xls"),
]
