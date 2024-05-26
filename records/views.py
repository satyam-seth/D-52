from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView, View

from accounts.mixins import RoomRequiredMixin
from accounts.models import Room
from core.excel import get_excel
from records.forms import RecordForm, WaterFrom
from records.models import Electricity, Maid, Record, Water

# from core.notification import notify_record, notify_water


User = get_user_model()


class AddTemplateView(LoginRequiredMixin, RoomRequiredMixin, TemplateView):
    """View to render record and water form"""

    template_name = "records/add.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        room_id = self.get_room_id(self.request)
        assert room_id
        room = Room.objects.get(id=room_id)
        record_form = RecordForm(
            label_suffix="",
            room=room,
            initial={"purchaser": self.request.user},
        )
        water_form = WaterFrom(label_suffix="")
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "add_active": "active",
                "record_form": record_form,
                "water_form": water_form,
            }
        )
        return context


class RecordAddView(LoginRequiredMixin, RoomRequiredMixin, View):
    """View save record form data"""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Method to validate and save record form post data"""

        room_id = self.get_room_id(self.request)
        assert room_id
        room = Room.objects.get(id=room_id)
        form = RecordForm(data=request.POST, room=room)
        if form.is_valid():
            room_id = self.get_room_id(self.request)
            assert room_id
            room = Room.objects.get(id=room_id)
            reg = form.save(commit=False)
            reg.adder = request.user
            reg.room = room
            reg.save()
            messages.success(request, "Your item record successfully added.")
            # TODO: move this logic in record post save signal
            # notify_record(reg.id)
        else:
            messages.error(
                request,
                "Please check and fill all information correctly, Your item record not added.",
            )
        return redirect("records:add")


class WaterAddView(LoginRequiredMixin, RoomRequiredMixin, View):
    """View save water form data"""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Method to validate and save water form post data"""

        form = WaterFrom(request.POST)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.adder = request.user
            reg.save()
            messages.success(request, "Water record successfully added.")
            # TODO: move this logic in water post save signal
            # notify_record(reg.id)
        else:
            messages.error(
                request,
                "Please check and fill all information correctly, Water record not added.",
            )
        return redirect("records:add")


class RecordListView(LoginRequiredMixin, RoomRequiredMixin, ListView):
    """View to render list records"""

    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]
    extra_context = {"records_active": "active"}


# TODO: only show current user group data
class UserRecordListView(LoginRequiredMixin, RoomRequiredMixin, ListView):
    """View to render template to show records purchased by specific user"""

    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]

    # TODO: Add return type once this issue is fixed
    # - https://github.com/typeddjango/django-stubs/issues/477
    # def get_queryset(self) -> QuerySet[Any]:
    def get_queryset(self):
        queryset = super().get_queryset().filter(purchaser__id=self.kwargs["user_id"])
        return queryset


# TODO: only show current user group water records
class WaterListView(LoginRequiredMixin, RoomRequiredMixin, ListView):
    """View to render list of water records"""

    model = Water
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]


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


# TODO: only show current user group records
class SearchListView(LoginRequiredMixin, RoomRequiredMixin, ListView):
    """View to render search result record list"""

    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]
    template_name = "records/search.html"

    # TODO: Add return type once this issue is fixed
    # - https://github.com/typeddjango/django-stubs/issues/477
    # def get_queryset(self) -> QuerySet[Any]:
    def get_queryset(self):
        item_name_query = self.request.GET["query"]
        queryset = super().get_queryset().filter(item__icontains=item_name_query)

        return queryset


class DownloadTemplateView(LoginRequiredMixin, RoomRequiredMixin, TemplateView):
    """View to render download template"""

    template_name = "records/download.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        # TODO: remove hardcoded group name
        users = User.objects.filter(groups__name__in=["d52"])

        context = super().get_context_data(**kwargs)
        context["users"] = users
        context["download_active"] = "active"
        return context


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
