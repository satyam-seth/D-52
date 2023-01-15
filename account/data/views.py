from typing import Any, Dict

import xlwt  # type: ignore
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, ListView, View

from .forms import RecordFrom, WaterFrom
from .models import Record, Water
from .notification import notify_record, notify_water

User = get_user_model()

# TODO: use login required decorator
class AddTemplateView(TemplateView):
    template_name = "data/add.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        record_form = RecordFrom(label_suffix="")
        water_form = WaterFrom(label_suffix="")
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "add_active": "active",
                "add_disabled": "disabled",
                "record_form": record_form,
                "water_form": water_form,
            }
        )
        return context


# TODO: use login required decorator
class RecordAddView(View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest):
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
        return redirect("add")


# TODO: use login required decorator
def add_water(request):
    # TODO: use require_http_methods for only post
    if request.method == "POST":
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
        return redirect("add")


class RecordListView(ListView):
    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["records_active"] = "active"
        context["records_disabled"] = "disabled"
        return context


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

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["user"] = User.objects.get(pk=self.kwargs["user_id"])
        return context


# TODO: only show current user group water records
class WaterListView(ListView):
    model = Water
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]


# TODO: fix this view
def report(request):
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
        "report_disabled": "disabled",
        "total_records": total_records,
        "total_price": total_price,
        "per_user_price": per_user_price,
        "each_user_records": each_user_records,
    }
    return render(request, "data/report.html", context)


# TODO:only show current user group records
class SearchListView(ListView):
    model = Record
    paginate_by = 20
    paginate_orphans = 10
    ordering = ["-purchase_date"]
    template_name = "data/search.html"

    # TODO: Add return type once this issue is fixed - https://github.com/typeddjango/django-stubs/issues/477
    # def get_queryset(self) -> QuerySet[Any]:
    def get_queryset(self):
        queryset = Record.objects.filter(item__icontains=self.request.GET["query"])
        return queryset


def download(request):
    context = {"download_active": "active", "download_disabled": "disabled"}
    return render(request, "data/download.html", context)


# TODO: fix this view
def overall_xls(request):
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


def user_xls(request, user):
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
