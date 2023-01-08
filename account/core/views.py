from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetCompleteView
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from data.models import Record, Water

from .forms import FeedbackFrom, LoginForm
from .models import Electricity, Feedback, Maid

# Create your views here.


def home(request):
    # TODO: handle empty database state
    w_sum = Water.objects.aggregate(Sum("quantity"))["quantity__sum"]
    w_price = 40 * w_sum
    w_pp = w_price / 4

    # TODO: handle empty database state
    electricity = Electricity.objects.latest("due_date")
    e_pp = electricity.price / 4
    e_days_left = (electricity.due_date - timezone.now().date()).days

    # TODO: handle empty database state
    maid = Maid.objects.latest("due_date")
    m_pp = maid.price / 4
    m_days_left = (maid.due_date - timezone.now().date()).days

    # TODO: remove hardcoded user id
    # user id 2 is satyam
    satyam_record = Record.objects.filter(purchaser__id=2)
    st_price = satyam_record.aggregate(Sum("price"))["price__sum"]
    st_items = len(satyam_record)

    # user id 3 is ankit
    ankit_record = Record.objects.filter(purchaser__id=3)
    at_price = ankit_record.aggregate(Sum("price"))["price__sum"]
    at_items = len(ankit_record)

    # user id 4 is pranshant
    prashant_record = Record.objects.filter(purchaser__id=4)
    pt_price = prashant_record.aggregate(Sum("price"))["price__sum"]
    pt_items = len(prashant_record)

    # user id 5 is ganga
    ganga_record = Record.objects.filter(purchaser__id=5)
    gt_price = ganga_record.aggregate(Sum("price"))["price__sum"]
    gt_items = len(ganga_record)

    context = {
        "home_active": "active",
        "home_disabled": "disabled",
        "w_sum": w_sum,
        "w_price": w_price,
        "w_pp": w_pp,
        "electricity": electricity,
        "e_pp": e_pp,
        "e_days_left": e_days_left,
        "maid": maid,
        "m_pp": m_pp,
        "m_days_left": m_days_left,
        "st_price": st_price,
        "st_items": st_items,
        "at_price": at_price,
        "at_items": at_items,
        "gt_price": gt_price,
        "gt_items": gt_items,
        "pt_price": pt_price,
        "pt_items": pt_items,
    }

    return render(request, "core/index.html", context)


def about(request):
    context = {"about_active": "active", "about_disabled": "disabled"}
    return render(request, "core/about.html", context)


def feedback(request):
    if request.method == "POST":
        fm = FeedbackFrom(request.POST)
        if fm.is_valid():
            nm = fm.cleaned_data["name"]
            tp = fm.cleaned_data["problem"]
            mg = fm.cleaned_data["message"]
            current_dt = timezone.now()
            reg = Feedback(name=nm, problem=tp, message=mg, datetime=current_dt)
            reg.save()
            messages.success(
                request,
                "Thank you for your valuable feedback, it will help us to improve your experience.",
            )
        return redirect("home")
    else:
        fm = FeedbackFrom()

    context = {"feedback_active": "active", "feedback_disabled": "disabled", "form": fm}
    return render(request, "core/feedback.html", context)


def search(request):
    query = request.GET["query"]
    if len(query) > 50 or len(query) == 0:
        results = Record.objects.none()
    else:
        results = Record.objects.filter(item__icontains=query)
    return render(request, "core/search.html", {"records": results})


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = LoginForm(request=request, data=request.POST)
            if form.is_valid():
                uname = form.cleaned_data["username"]
                upass = form.cleaned_data["password"]
                user = authenticate(username=uname, password=upass)
                if user is not None:
                    login(request, user)
                messages.success(request, "Logged In Successfully !!")
                return redirect("home")
        else:
            form = LoginForm()
        context = {"form": form, "login_active": "active", "login_disabled": "disabled"}
        return render(request, "core/login.html", context)
    else:
        return redirect("home")


def user_logout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully !!")
    return redirect("home")


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = "/login/"
        return context
