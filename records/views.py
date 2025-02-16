import io
from typing import Any, Dict, Optional

import pandas as pd
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, TemplateView, View

from accounts.mixins import RoomRequiredMixin
from records.export import RoomExporter
from records.forms import RecordForm, WaterForm
from records.models import Record, Water

# from core.notification import notify_record, notify_water


User = get_user_model()


class DashboardTemplateView(RoomRequiredMixin, TemplateView):
    """Dashboard template view"""

    template_name = "records/dashboard.html"

    # TODO: finalize it
    # def get_electricity_context(self, room_id: int):
    #     """Returns electricity context"""

    #     # TODO: handle empty database state
    #     electricity = None
    #     try:
    #         electricity = Electricity.objects.latest("due_date")
    #         e_pp = electricity.price / 4
    #         # TODO: add this filed as model property
    #         e_days_left = (electricity.due_date - timezone.now().date()).days
    #     except ObjectDoesNotExist:
    #         e_pp, e_days_left = 0, 0

    # TODO: finalize it
    # def get_maid_context(self, room_id: int):
    #     """Returns maid context"""

    #     # TODO: handle empty database state
    #     maid = None
    #     try:
    #         maid = Maid.objects.latest("due_date")
    #         m_pp = maid.price / 4
    #         # TODO: add this filed as model property
    #         m_days_left = (maid.due_date - timezone.now().date()).days
    #     except ObjectDoesNotExist:
    #         m_pp, m_days_left = 0, 0

    def get_water_context(self, room_id: int):
        """Returns water context"""

        total_quantity = 0
        waters = Water.objects.filter(room_id=room_id)

        if waters:
            total_quantity = waters.aggregate(Sum("quantity"))["quantity__sum"]

        return {"water_quantity": total_quantity}

    def get_room_members_context(self, room_id: int):
        """Returns room members context"""

        room_members = User.objects.filter(room_membership__room_id=room_id)
        room_members_context = []

        for room_member in room_members:
            room_member_records = Record.objects.filter(
                room_id=room_id,
                purchaser=room_member,
            )
            records_count = room_member_records.count()
            room_member_total_spent = room_member_records.aggregate(Sum("price"))[
                "price__sum"
            ]
            total_spent = room_member_total_spent if room_member_total_spent else 0
            room_members_context.append(
                {
                    "member": room_member,
                    "records_count": records_count,
                    "total_spent": total_spent,
                }
            )

        return {"room_members_data": room_members_context}

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        room_id = self.get_room_id(self.request)
        assert room_id

        context = super().get_context_data(**kwargs)
        context["dashboard_active"] = "active"
        context.update(self.get_water_context(room_id))
        context.update(self.get_room_members_context(room_id))
        return context


class AddDataView(RoomRequiredMixin, View):
    """View to render and handle record and water form"""

    def get_record_form(self) -> RecordForm:
        """Returns an empty record form"""

        return RecordForm(
            label_suffix="",
            room_id=self.get_room_id(self.request),
            initial={"purchaser": self.request.user},
        )

    def get_water_form(self) -> WaterForm:
        """Returns an water empty form"""

        return WaterForm(label_suffix="")

    def get_context(
        self,
        record_form: Optional[RecordForm] = None,
        water_form: Optional[WaterForm] = None,
    ) -> dict[str, Any]:
        """Returns context"""

        _record_form = record_form if record_form else self.get_record_form()
        _water_form = water_form if water_form else self.get_water_form()

        context = {
            "add_active": "active",
            "record_form": _record_form,
            "water_form": _water_form,
        }
        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render record and water form"""

        context = self.get_context()
        return render(request, "records/add_data.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle record and water form submission"""

        context: Dict[str, Any]
        room_id = self.get_room_id(self.request)

        if "record_submit" in request.POST:
            record_form = RecordForm(data=request.POST, room_id=room_id)

            if record_form.is_valid():
                reg = record_form.save(commit=False)
                reg.adder = request.user
                reg.room = self.get_room(self.request)
                reg.save()
                messages.success(request, "Your item record successfully added.")
                context = self.get_context()
                # TODO: move this logic in record post save signal
                # notify_record(reg.id)
            else:
                messages.error(request, "Your item record not added.")
                context = self.get_context(record_form=record_form)

        elif "water_submit" in request.POST:
            water_form = WaterForm(request.POST)

            if water_form.is_valid():
                reg = water_form.save(commit=False)
                reg.adder = request.user
                reg.room = self.get_room(self.request)

                try:
                    reg.save()
                    messages.success(request, "Water record successfully added.")
                    context = self.get_context()
                    # TODO: move this logic in water post save signal
                    # notify_record(reg.id)
                except ValidationError as e:
                    messages.warning(request, e.message)
                    context = self.get_context(water_form=water_form)
            else:
                messages.error(request, "Water record not added.")
                context = self.get_context(water_form=water_form)
        else:
            messages.error(
                request,
                "Please check and fill in all information correctly.",
            )
            context = self.get_context()

        return render(request, "records/add_data.html", context)


class RecordListView(RoomRequiredMixin, ListView):
    """View to render list records"""

    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_datetime"]

    def get_queryset(self):
        room_id = self.get_room_id(self.request)
        member_id = self.kwargs.get("member_id")
        item_name_query = self.request.GET.get("query")
        queryset = super().get_queryset().filter(room_id=room_id)

        if member_id:
            queryset = queryset.filter(purchaser_id=member_id)

        if item_name_query:
            queryset = queryset.filter(item__icontains=item_name_query)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        member_id = self.kwargs.get("member_id")
        item_name_query = self.request.GET.get("query")
        context = super().get_context_data(**kwargs)

        if member_id:
            context["member_id"] = member_id
        elif item_name_query:
            context["search_records"] = item_name_query
            context["records_active"] = "active"
        else:
            context["records_active"] = "active"
            context["room_records"] = True

        return context


class WaterListView(RoomRequiredMixin, ListView):
    """View to render list of water records"""

    model = Water
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]

    def get_queryset(self):
        room_id = self.get_room_id(self.request)
        queryset = super().get_queryset().filter(room_id=room_id)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["waters_active"] = "active"
        return context


class ExportDataView(RoomRequiredMixin, ListView):
    """View to render export data template"""

    model = User
    ordering = ["-id"]
    paginate_by = 20
    paginate_orphans = 10
    context_object_name = "room_member_list"
    template_name = "records/export_data.html"

    def get_queryset(self):
        room_id = self.get_room_id(self.request)
        queryset = super().get_queryset().filter(room_membership__room_id=room_id)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["export_data_active"] = "active"
        return context


class RoomReportView(RoomRequiredMixin, View):
    """View to for room report"""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Calculate and render report template"""

        room_id = self.get_room_id(self.request)
        assert room_id

        room_members = User.objects.filter(room_membership__room_id=room_id)
        room_records = Record.objects.filter(room_id=room_id)
        room_records_count = room_records.count()
        total_price = room_records.aggregate(Sum("price"))["price__sum"]
        room_total_price = total_price if total_price else 0
        per_member_price = room_total_price / room_members.count()

        room_members_report = []
        for room_member in room_members:
            room_member_records = room_records.filter(purchaser=room_member)
            records_count = room_member_records.count()
            room_member_total_spent = room_member_records.aggregate(Sum("price"))[
                "price__sum"
            ]
            total_spent = room_member_total_spent if room_member_total_spent else 0
            price_diff = per_member_price - (total_spent if total_spent else 0)

            room_members_report.append(
                {
                    "room_member": room_member,
                    "total_spent": total_spent,
                    "price_diff": price_diff,
                    "records_count": records_count,
                }
            )

        context = {
            "room_reports_active": "active",
            "room_records_count": room_records_count,
            "room_total_price": room_total_price,
            "per_member_price": per_member_price,
            "room_members_report": room_members_report,
        }

        return render(request, "records/room_reports.html", context)


class BaseExportView(RoomRequiredMixin, View):
    """Base view for exporting data."""

    def write_to_sheet(self, writer, sheet_name: str, data: pd.DataFrame) -> None:
        """
        Helper function to write a DataFrame to an Excel sheet
        """
        # TODO: Add sheet styling
        data.to_excel(writer, sheet_name=sheet_name, index=False)

    def get_room_and_export_instance(self, request) -> tuple:
        """Fetch room details and initialize RoomExportData."""

        room = self.get_room(self.request)
        exporter = RoomExporter(room.id)
        return room, exporter

    def generate_excel_buffer(
        self,
        data: list[tuple[str, pd.DataFrame]],
    ) -> io.BytesIO:
        """Generates a single in-memory Excel file from a list of DataFrames with sheet names"""

        # Create an in-memory buffer for the Excel file
        buffer = io.BytesIO()

        # Use pd.ExcelWriter to create an Excel file
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            for sheet_name, df in data:
                self.write_to_sheet(writer, sheet_name, df)

        # Reset buffer position for reading
        buffer.seek(0)

        return buffer

    def generate_excel_response(
        self,
        file_name: str,
        buffer: io.BytesIO,
    ) -> HttpResponse:
        """Generate and return an Excel response."""

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={file_name}.xlsx"
        return response

    def get_file_response(self, file_name: str, data: list[tuple[str, pd.DataFrame]]):
        """Generates an Excel file response from a list of DataFrames with sheet names"""

        buffer = self.generate_excel_buffer(data)
        response = self.generate_excel_response(file_name, buffer)
        return response


class ExportAllView(BaseExportView):
    """View for exporting room all data"""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handles POST requests to export room all data"""

        room, exporter = self.get_room_and_export_instance(request)

        # Prepare room members data
        room_members_data = []
        room_members = User.objects.filter(room_membership__room=room)
        for room_member in room_members:
            member_name = room_member.get_full_name()
            member_data_df = exporter.get_record_df(purchaser=room_member)
            room_members_data.append((member_name, member_data_df))

        # Combine all data into a single list
        data = [
            ("All Records", exporter.get_record_df()),
            *room_members_data,
            ("Water Records", exporter.get_water_df()),
            ("Maid Records", exporter.get_maid_df()),
            ("Electricity Records", exporter.get_electricity_df()),
        ]

        file_name = f"{room.name}_all_data"
        return self.get_file_response(file_name, data)


class ExportAllRecordView(BaseExportView):
    """View for exporting room all record data"""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handles POST requests to export room all record data"""

        room, exporter = self.get_room_and_export_instance(request)
        data = [("All Records", exporter.get_record_df())]

        file_name = f"{room.name}_all_records_data"
        return self.get_file_response(file_name, data)


class ExportMemberRecordView(BaseExportView):
    """View for exporting room member records data"""

    def post(self, request: HttpRequest, member_id: int) -> HttpResponse:
        """Handles POST requests to export room member records data"""

        room, exporter = self.get_room_and_export_instance(request)
        room_member = get_object_or_404(User, pk=member_id)

        member_name = room_member.get_full_name()
        member_df = exporter.get_record_df(purchaser=room_member)
        data = [(member_name, member_df)]

        file_name = f"{room.name}_{member_name}_records_data"
        return self.get_file_response(file_name, data)


class ExportWaterView(BaseExportView):
    """View for exporting room water data"""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handles POST requests to export room water data"""

        room, exporter = self.get_room_and_export_instance(request)
        data = [("Water Records", exporter.get_water_df())]

        file_name = f"{room.name}_water_data"
        return self.get_file_response(file_name, data)


class ExportMaidView(BaseExportView):
    """View for exporting room maid data"""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handles POST requests to export room maid data"""

        room, exporter = self.get_room_and_export_instance(request)
        data = [("Maid Records", exporter.get_maid_df())]

        file_name = f"{room.name}_maid_data"
        return self.get_file_response(file_name, data)


class ExportElectricityView(BaseExportView):
    """View for exporting room electricity data"""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handles POST requests to export room electricity data"""

        room, exporter = self.get_room_and_export_instance(request)
        data = [("Electricity Records", exporter.get_electricity_df())]

        file_name = f"{room.name}_electricity_data"
        return self.get_file_response(file_name, data)
