import xlwt  # type: ignore
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import RecordFrom, WaterFrom
from .models import Record, Water
from .notification import notify_record, notify_water

User = get_user_model()

# TODO: use login required decorator
def add(request):
    if request.user.is_authenticated:
        record_form = RecordFrom(label_suffix="")
        water_form = WaterFrom(label_suffix="")
        context = {
            "add_active": "active",
            "add_disabled": "disabled",
            "record_form": record_form,
            "water_form": water_form,
        }
        return render(request, "data/add.html", context)
    else:
        return redirect("login")


# TODO: use login required decorator
def add_item(request):
    # TODO: use require_http_methods for only post
    if request.method == "POST":
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


# TODO: user ListView paginated_by attribute
def records(request):
    # TODO: expose only requested user group records
    records = Record.objects.all().order_by("-purchase_date")
    paginator = Paginator(records, 20, orphans=10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "records_active": "active",
        "records_disabled": "disabled",
        "records": page_obj,
    }
    return render(request, "data/records.html", context)


# TODO: use list view with paginator
def detailed_view(request, user_id):
    user = User.objects.get(pk=user_id)
    records = Record.objects.filter(purchaser__id=user_id).order_by("-purchase_date")
    return render(request, "data/detailed.html", {"records": records, "user": user})


# TODO: use list view with paginator
def detailed_water_view(request):
    records = Water.objects.all().order_by("-purchase_date")
    return render(request, "data/detailed_water.html", {"records": records})


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


def search(request):
    query = request.GET["query"]
    results = Record.objects.filter(item__icontains=query)
    return render(request, "data/search.html", {"records": results})


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
