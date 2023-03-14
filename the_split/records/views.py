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
from records.models import Record, Water

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


# TODO: fix this view
# TODO: Add login required once user group login achieved
def overall_xls(request: HttpRequest) -> HttpResponse:
    records = Record.objects.all().order_by("date")
    data = []
    for record in records:
        temp = [
            record.date.strftime("%d-%m-%Y"),
            record.item,
            record.price,
            record.name,
            record.id,
            record.datetime.strftime("%d-%m-%Y"),
            record.added_by,
        ]
        data.append(temp)

    file_name = "Overall Items Records.xls"
    with open(file_name, "wb") as f:
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = "attachment; filename=" + file_name
        wb = xlwt.Workbook(encoding="utf-8")
        ws = wb.add_sheet("Overall Items Records")
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = [
            "Date",
            "Item Name",
            "Price",
            "Purchase By",
            "Entry ID",
            "Entry Date",
            "Added By",
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        for row in data:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        wb.save(response)
        return response


# TODO: Fix this view
# TODO: Add login required once user group login achieved
def user_xls(request: HttpRequest, user: str) -> HttpResponse:
    records = Record.objects.filter(name=user).order_by("date")
    data = []
    for record in records:
        temp = [
            record.date.strftime("%d-%m-%Y"),
            record.item,
            record.price,
            record.id,
            record.datetime.strftime("%d-%m-%Y"),
            record.added_by,
        ]
        data.append(temp)

    file_name = user + " Items Records.xls"
    with open(file_name, "wb") as f:
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = "attachment; filename=" + file_name
        wb = xlwt.Workbook(encoding="utf-8")
        ws = wb.add_sheet(f"{user} Records")
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ["Date", "Item Name", "Price", "Entry ID", "Entry Date", "Added By"]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        for row in data:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        wb.save(response)
        return response


# TODO: fix this view
# TODO: Add login required once user group login achieved
# def water_xls(request):
#     records = Water.objects.all().order_by('date')
#     data=[]
#     for record in records:
#         temp=[record.date.strftime("%d-%m-%Y"),record.quantity,record.id,record.datetime.strftime("%d-%m-%Y"),record.added_by]
#         data.append(temp)

#     file_name='Water Records.xls'
#     with open(file_name, 'wb') as f:
#         response = HttpResponse(content_type='application/ms-excel')
#         response['Content-Disposition'] = 'attachment; filename='+file_name
#         wb = xlwt.Workbook(encoding='utf-8')
#         ws = wb.add_sheet('Water Records')
#         row_num = 0
#         font_style = xlwt.XFStyle()
#         font_style.font.bold = True
#         columns = ['Date','Quantity','Entry ID','Entry Date','Added By']
#         for col_num in range(len(columns)):
#             ws.write(row_num, col_num, columns[col_num], font_style)
#         font_style = xlwt.XFStyle()
#         for row in data:
#             row_num += 1
#             for col_num in range(len(row)):
#                 ws.write(row_num, col_num, row[col_num], font_style)
#         wb.save(response)
#         return response
