import xlwt  # type: ignore
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from core.models import Electricity, Maid

from .forms import RecordFrom, WaterFrom
from .models import Record, Water
from .notification import notify_record, notify_water

# Create your views here.

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
            dt = fm.cleaned_data["date"]
            qt = fm.cleaned_data["quantity"]
            current_dt = timezone.now()
            full_name = request.user.get_full_name()
            reg = Water.objects.create(
                date=dt, quantity=qt, datetime=current_dt, added_by=full_name
            )
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


def detailed_view(request, var):
    if var == "satyam":
        data = Record.objects.filter(name="Satyam Seth").order_by("date")

    elif var == "ankit":
        data = Record.objects.filter(name="Ankit Kumar Gupta").order_by("date")

    elif var == "ganga":
        data = Record.objects.filter(name="Ganga Sagar Bharti").order_by("date")

    elif var == "prashant":
        data = Record.objects.filter(name="Prashant Kumar Yadav").order_by("date")

    else:
        data = Water.objects.all().order_by("date")

    return render(request, "data/detailed.html", {"records": data, "var": var})


def report(request):
    record = Record.objects.all()
    t_items = len(record)
    t_price = record.aggregate(Sum("price"))["price__sum"]
    p_price = t_price / 4

    satyam_record = Record.objects.filter(name="Satyam Seth")
    st_items = len(satyam_record)
    st_price = satyam_record.aggregate(Sum("price"))["price__sum"]
    sd_price = p_price - st_price

    ankit_record = Record.objects.filter(name="Ankit Kumar Gupta")
    at_items = len(ankit_record)
    at_price = ankit_record.aggregate(Sum("price"))["price__sum"]
    ad_price = p_price - at_price

    ganga_record = Record.objects.filter(name="Ganga Sagar Bharti")
    gt_items = len(ganga_record)
    gt_price = ganga_record.aggregate(Sum("price"))["price__sum"]
    gd_price = p_price - gt_price

    prashant_record = Record.objects.filter(name="Prashant Kumar Yadav")
    pt_items = len(prashant_record)
    pt_price = prashant_record.aggregate(Sum("price"))["price__sum"]
    pd_price = p_price - pt_price

    context = {
        "report_active": "active",
        "report_disabled": "disabled",
        "t_items": t_items,
        "t_price": t_price,
        "p_price": p_price,
        "st_items": st_items,
        "st_price": st_price,
        "sd_price": sd_price,
        "at_items": at_items,
        "at_price": at_price,
        "ad_price": ad_price,
        "gt_items": gt_items,
        "gt_price": gt_price,
        "gd_price": gd_price,
        "pt_items": pt_items,
        "pt_price": pt_price,
        "pd_price": pd_price,
    }
    return render(request, "data/report.html", context)


def search(request):
    query = request.GET["query"]
    results = Record.objects.filter(item__icontains=query)
    return render(request, "data/search.html", {"records": results})


def download(request):
    context = {"download_active": "active", "download_disabled": "disabled"}
    return render(request, "data/download.html", context)


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
