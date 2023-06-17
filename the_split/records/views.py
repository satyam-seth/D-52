from typing import Any, Dict

import xlwt  # type: ignore
from core.notification import notify_record, notify_water
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView, View
from records.forms import RecordFrom, WaterFrom
from records.models import Electricity, Maid, Record, Water

User = get_user_model()


class AddTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "records/add.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        record_form = RecordFrom(label_suffix="")
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


class RecordAddView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest) -> HttpResponse:
        fm = RecordFrom(request.POST)
        if fm.is_valid():
            reg = fm.save(commit=False)
            reg.adder = request.user
            reg.save()
            messages.success(request, "Your item record successfully added.")
            notify_record(reg.id)
        else:
            messages.error(
                request,
                "Please check and fill all information correctly, Your item record not added.",
            )
        return redirect("records:add")


class WaterAddView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest) -> HttpResponse:
        fm = WaterFrom(request.POST)
        if fm.is_valid():
            reg = fm.save(commit=False)
            reg.adder = request.user
            reg.save()
            messages.success(request, "Water record successfully added.")
            notify_water(reg.id)
        else:
            messages.error(
                request,
                "Please check and fill all information correctly, Water record not added.",
            )
        return redirect("records:add")


# TODO: Add login required once user group login achieved
class RecordListView(ListView):
    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]
    extra_context = {"records_active": "active"}


# TODO: Add login required once user group login achieved and only show current user group data
class UserRecordListView(ListView):
    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]

    # TODO: Add return type once this issue is fixed - https://github.com/typeddjango/django-stubs/issues/477
    # def get_queryset(self) -> QuerySet[Any]:
    def get_queryset(self):
        queryset = Record.objects.filter(purchaser__id=self.kwargs["user_id"]).order_by(
            "-purchase_date"
        )
        return queryset


# TODO: only show current user group water records
class WaterListView(ListView):
    model = Water
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]


# TODO: fix this view
# TODO: Add login required once user group login achieved
def report(request: HttpRequest) -> HttpResponse:
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
# TODO: Add login required once user group login achieved
class SearchListView(ListView):
    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]
    template_name = "records/search.html"

    # TODO: Add return type once this issue is fixed - https://github.com/typeddjango/django-stubs/issues/477
    # def get_queryset(self) -> QuerySet[Any]:
    def get_queryset(self):
        queryset = Record.objects.filter(item__icontains=self.request.GET["query"])
        return queryset


# TODO: Add login required once user group login achieved
class DownloadTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "records/download.html"
    extra_context = {"download_active": "active"}

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        # TODO: remove hardcoded group name
        users = User.objects.filter(groups__name__in=["d52"])

        context = super().get_context_data(**kwargs)
        context["users"] = users
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
            purchaser_name if purchaser_name else record.purchaser.username,
            record.id,
            record.created_on.strftime("%d-%m-%Y"),
            record.created_on.strftime("%H:%M:%S"),
            adder_name if adder_name else record.adder.username,
        ]
        data.append(temp)

    # crate response object
    file_name = "Overall Items Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # create workbook and add sheet
    workbook = xlwt.Workbook(encoding="utf-8")
    workbook_sheet = workbook.add_sheet("Overall Items Records")

    # add columns
    columns = [
        "Purchase Date",
        "Item Name",
        "Price",
        "Purchase By",
        "Entry ID",
        "Entry Date",
        "Entry Time",
        "Added By",
    ]
    header_style = xlwt.easyxf("font: bold on")
    for col_num, column in enumerate(columns):
        workbook_sheet.write(0, col_num, column, header_style)

    # add rows
    data_style = xlwt.XFStyle()
    for row_num, row in enumerate(data, start=1):
        for col_num, value in enumerate(row):
            workbook_sheet.write(row_num, col_num, value, data_style)

    # save workbook and return response
    workbook.save(response)
    return response


# TODO: Fix this view
# TODO: Add login required once user group login achieved
def user_xls(request: HttpRequest, user_id: int) -> HttpResponse:
    """View to download user report excel file"""

    # query data from db
    purchaser = User.objects.get(pk=user_id)
    purchaser_name = (
        purchaser.get_full_name() if purchaser.get_full_name() else purchaser.username
    )
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
            adder_name if adder_name else record.adder.username,
        ]
        data.append(temp)

    # crate response object
    file_name = f"{purchaser_name} Items Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # create workbook and add sheet
    workbook = xlwt.Workbook(encoding="utf-8")
    workbook_sheet = workbook.add_sheet(f"{purchaser_name} Records")

    # add columns
    columns = [
        "Date",
        "Item Name",
        "Price",
        "Entry ID",
        "Entry Date",
        "Entry Time",
        "Added By",
    ]
    header_style = xlwt.easyxf("font: bold on")
    for col_num, column in enumerate(columns):
        workbook_sheet.write(0, col_num, column, header_style)

    # add rows
    data_style = xlwt.XFStyle()
    for row_num, row in enumerate(data, start=1):
        for col_num, value in enumerate(row):
            workbook_sheet.write(row_num, col_num, value, data_style)

    # save workbook and return response
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
            adder_name if adder_name else record.adder.username,
        ]
        data.append(temp)

    # crate response object
    file_name = "Water Entry Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # create workbook and add sheet
    workbook = xlwt.Workbook(encoding="utf-8")
    workbook_sheet = workbook.add_sheet("Water Entry Records")

    # add columns
    columns = [
        "Date",
        "Quantity",
        "Entry ID",
        "Entry Date",
        "Entry Time",
        "Added By",
    ]
    header_style = xlwt.easyxf("font: bold on")
    for col_num, column in enumerate(columns):
        workbook_sheet.write(0, col_num, column, header_style)

    # add rows
    data_style = xlwt.XFStyle()
    for row_num, row in enumerate(data, start=1):
        for col_num, value in enumerate(row):
            workbook_sheet.write(row_num, col_num, value, data_style)

    # save workbook and return response
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
        ]
        data.append(temp)

    # crate response object
    file_name = "Electricity Bill Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # create workbook and add sheet
    workbook = xlwt.Workbook(encoding="utf-8")
    workbook_sheet = workbook.add_sheet("Electricity Bill Records")

    # add columns
    columns = [
        "Date",
        "Price",
        "Entry ID",
        "Entry Date",
        "Entry Time",
    ]
    header_style = xlwt.easyxf("font: bold on")
    for col_num, column in enumerate(columns):
        workbook_sheet.write(0, col_num, column, header_style)

    # add rows
    data_style = xlwt.XFStyle()
    for row_num, row in enumerate(data, start=1):
        for col_num, value in enumerate(row):
            workbook_sheet.write(row_num, col_num, value, data_style)

    # save workbook and return response
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
        ]
        data.append(temp)

    # crate response object
    file_name = "Maid Salary Records.xls"
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename={file_name}"

    # create workbook and add sheet
    workbook = xlwt.Workbook(encoding="utf-8")
    workbook_sheet = workbook.add_sheet("Maid Salary Records")

    # add columns
    columns = [
        "Date",
        "Price",
        "Entry ID",
        "Entry Date",
        "Entry Time",
    ]
    header_style = xlwt.easyxf("font: bold on")
    for col_num, column in enumerate(columns):
        workbook_sheet.write(0, col_num, column, header_style)

    # add rows
    data_style = xlwt.XFStyle()
    for row_num, row in enumerate(data, start=1):
        for col_num, value in enumerate(row):
            workbook_sheet.write(row_num, col_num, value, data_style)

    # save workbook and return response
    workbook.save(response)
    return response
