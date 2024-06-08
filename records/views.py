from typing import Any, Dict, Optional

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, View

from accounts.mixins import RoomRequiredMixin
from accounts.models import Room
from core.excel import get_excel
from records.forms import RecordForm, WaterForm
from records.models import Electricity, Maid, Record, Water

# from core.notification import notify_record, notify_water


User = get_user_model()


class AddDataView(LoginRequiredMixin, RoomRequiredMixin, View):
    """View to render and handle record and water form"""

    def get_room(self) -> Room:
        """Returns room"""

        room_id = self.get_room_id(self.request)
        assert room_id
        room = Room.objects.get(id=room_id)
        return room

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
                reg.room = self.get_room()
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
                reg.room = self.get_room()

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


class RecordListView(LoginRequiredMixin, RoomRequiredMixin, ListView):
    """View to render list records"""

    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]

    def get_queryset(self):
        room_id = self.get_room_id(self.request)
        user_id = self.kwargs.get("user_id")
        item_name_query = self.request.GET.get("query")
        queryset = super().get_queryset().filter(room__id=room_id)

        if user_id:
            queryset = queryset.filter(purchaser__id=user_id)

        if item_name_query:
            queryset = queryset.filter(item__icontains=item_name_query)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        user_id = self.kwargs.get("user_id")
        item_name_query = self.request.GET.get("query")
        context = super().get_context_data(**kwargs)

        if user_id:
            context["user_records"] = user_id
        elif item_name_query:
            context["search_records"] = item_name_query
            context["records_active"] = "active"
        else:
            context["records_active"] = "active"
            context["room_records"] = True

        return context


class WaterListView(LoginRequiredMixin, RoomRequiredMixin, ListView):
    """View to render list of water records"""

    model = Water
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]

    def get_queryset(self):
        room_id = self.get_room_id(self.request)
        queryset = super().get_queryset().filter(room__id=room_id)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["waters_active"] = "active"
        return context


class ExportDataView(LoginRequiredMixin, RoomRequiredMixin, ListView):
    """View to render export data template"""

    model = User
    ordering = ["-id"]
    paginate_by = 20
    paginate_orphans = 10
    context_object_name = "room_member_list"
    template_name = "records/export_data.html"

    def get_queryset(self):
        room_id = self.get_room_id(self.request)
        queryset = super().get_queryset().filter(room_membership__room__id=room_id)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["export_data_active"] = "active"
        return context


# TODO: fix this view
# TODO: Add login required once user group login achieved
def report(request: HttpRequest) -> HttpResponse:
    """View to calculate and render report"""

    # TODO: remove hardcoded group name
    users = User.objects.filter(groups__name="d52")

    # TODO: get only current group records
    total_records = Record.objects.all()
    total_price = total_records.aggregate(Sum("price"))["price__sum"]
    per_user_price = total_price / users.count()

    # TODO: optimize this logic
    each_user_records = []
    for user in users:
        total_spent = total_records.filter(purchaser=user).aggregate(Sum("price"))[
            "price__sum"
        ]
        price_diif = per_user_price - (total_spent if total_spent else 0)
        each_user_records.append(
            {"user": user, "total_spent": total_spent, "price_diff": price_diif}
        )

    context = {
        "report_active": "active",
        "total_records": total_records,
        "total_price": total_price,
        "per_user_price": per_user_price,
        "each_user_records": each_user_records,
    }
    return render(request, "records/report.html", context)


# TODO: fix this view
# TODO: Add login required once user group login achieved
def overall_xls(request: HttpRequest) -> HttpResponse:
    """View to download overall report excel file"""

    # query data from db
    records = Record.objects.all().order_by("purchase_date")

    # prepare data
    data = []
    for record in records:
        adder_name = record.adder.get_full_name()
        purchaser_name = record.purchaser.get_full_name()
        temp = [
            record.purchase_date.strftime("%d-%m-%Y"),
            record.item,
            record.price,
            purchaser_name,
            record.id,
            record.created_on.strftime("%d-%m-%Y"),
            record.created_on.strftime("%H:%M:%S"),
            record.modified_on.strftime("%d-%m-%Y"),
            record.modified_on.strftime("%H:%M:%S"),
            adder_name,
        ]
        data.append(temp)

    # columns
    columns = [
        "Purchase Date",
        "Item Name",
        "Price",
        "Purchase By",
        "Entry ID",
        "Entry Date",
        "Entry Time",
        "Last Modified Date",
        "Last Modified Time",
        "Added By",
    ]

    # crate response object
    file_name = "Overall Items Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # save workbook and return response
    workbook = get_excel(sheet_name="Overall Items Records", columns=columns, data=data)
    workbook.save(response)
    return response


# TODO: Fix this view
# TODO: Add login required once user group login achieved
def user_xls(request: HttpRequest, user_id: int) -> HttpResponse:
    """View to download user report excel file"""

    # query data from db
    purchaser = User.objects.get(pk=user_id)
    purchaser_name = purchaser.get_full_name()
    records = Record.objects.filter(purchaser=purchaser).order_by("purchase_date")

    # prepare data
    data = []
    for record in records:
        adder_name = record.adder.get_full_name()
        temp = [
            record.purchase_date.strftime("%d-%m-%Y"),
            record.item,
            record.price,
            record.id,
            record.created_on.strftime("%d-%m-%Y"),
            record.created_on.strftime("%H:%M:%S"),
            record.modified_on.strftime("%d-%m-%Y"),
            record.modified_on.strftime("%H:%M:%S"),
            adder_name,
        ]
        data.append(temp)

    # columns
    columns = [
        "Date",
        "Item Name",
        "Price",
        "Entry ID",
        "Entry Date",
        "Entry Time",
        "Last Modified Date",
        "Last Modified Time",
        "Added By",
    ]

    # crate response object
    file_name = f"{purchaser_name} Items Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # save workbook and return response
    workbook = get_excel(f"{purchaser_name} Records", columns=columns, data=data)
    workbook.save(response)
    return response


# TODO: fix this view
# TODO: Add login required once user group login achieved
def water_xls(request: HttpRequest) -> HttpResponse:
    """View to download water report excel file"""

    # query data from db
    records = Water.objects.all().order_by("purchase_date")

    # prepare data
    data = []
    for record in records:
        adder_name = record.adder.get_full_name()
        temp = [
            record.purchase_date.strftime("%d-%m-%Y"),
            record.quantity,
            record.id,
            record.created_on.strftime("%d-%m-%Y"),
            record.created_on.strftime("%H:%M:%S"),
            record.modified_on.strftime("%d-%m-%Y"),
            record.modified_on.strftime("%H:%M:%S"),
            adder_name,
        ]
        data.append(temp)

    # columns
    columns = [
        "Date",
        "Quantity",
        "Entry ID",
        "Entry Date",
        "Entry Time",
        "Last Modified Date",
        "Last Modified Time",
        "Added By",
    ]

    # crate response object
    file_name = "Water Entry Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # save workbook and return response
    workbook = get_excel(sheet_name="Water Entry Records", columns=columns, data=data)
    workbook.save(response)
    return response


# TODO: fix this view
# TODO: Add login required once user group login achieved
def electricity_xls(request: HttpRequest) -> HttpResponse:
    """View to download electricity report excel file"""

    # query data from db
    records = Electricity.objects.all().order_by("due_date")

    # prepare data
    data = []
    for record in records:
        temp = [
            record.due_date.strftime("%d-%m-%Y"),
            record.price,
            record.id,
            record.created_on.strftime("%d-%m-%Y"),
            record.created_on.strftime("%H:%M:%S"),
            record.modified_on.strftime("%d-%m-%Y"),
            record.modified_on.strftime("%H:%M:%S"),
        ]
        data.append(temp)

    # columns
    columns = [
        "Date",
        "Price",
        "Entry ID",
        "Entry Date",
        "Entry Time",
        "Last Modified Date",
        "Last Modified Time",
    ]

    # crate response object
    file_name = "Electricity Bill Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # save workbook and return response
    workbook = get_excel(
        sheet_name="Electricity Bill Records",
        columns=columns,
        data=data,
    )
    workbook.save(response)
    return response


# TODO: fix this view
# TODO: Add login required once user group login achieved
def maid_xls(request: HttpRequest) -> HttpResponse:
    """View to download maid report excel file"""

    # query data from db
    records = Maid.objects.all().order_by("due_date")

    # prepare data
    data = []
    for record in records:
        temp = [
            record.due_date.strftime("%d-%m-%Y"),
            record.price,
            record.id,
            record.created_on.strftime("%d-%m-%Y"),
            record.created_on.strftime("%H:%M:%S"),
            record.modified_on.strftime("%d-%m-%Y"),
            record.modified_on.strftime("%H:%M:%S"),
        ]
        data.append(temp)

    # columns
    columns = [
        "Date",
        "Price",
        "Entry ID",
        "Entry Date",
        "Entry Time",
        "Last Modified Date",
        "Last Modified Time",
    ]

    # crate response object
    file_name = "Maid Salary Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # save workbook and return response
    workbook = get_excel(sheet_name="Maid Salary Records", columns=columns, data=data)
    workbook.save(response)
    return response
