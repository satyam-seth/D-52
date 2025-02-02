from django.urls import path

from records import views

app_name = "records"

urlpatterns = [
    path("dashboard/", views.DashboardTemplateView.as_view(), name="dashboard"),
    path("add_data/", views.AddDataView.as_view(), name="add_data"),
    path("records/", views.RecordListView.as_view(), name="records"),
    # TODO: rename to member_id
    path("records/<int:user_id>/", views.RecordListView.as_view(), name="user_records"),
    path("waters/", views.WaterListView.as_view(), name="waters"),
    path("export_data/", views.ExportDataView.as_view(), name="export_data"),
    path("room_reports/", views.RoomReportView.as_view(), name="room_reports"),
    path("export/all/", views.ExportAllView.as_view(), name="export_all"),
    path(
        "export/all/records/",
        views.ExportAllRecordView.as_view(),
        name="export_all_records",
    ),
    path(
        "export/records/<int:member_id>/",
        views.ExportMemberRecordView.as_view(),
        name="export_member_records",
    ),
    path("export/water/", views.ExportWaterView.as_view(), name="export_water"),
    path("electricity_xls/", views.electricity_xls, name="electricity_xls"),
    path("maid_xls/", views.maid_xls, name="maid_xls"),
]
