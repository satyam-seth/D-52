from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, TemplateView

# stop using this model in core once current index view changed as dashboard
from records.models import Electricity, Maid, Record, Water

from .forms import FeedbackFrom

# Create your views here.

User = get_user_model()


# TODO: fix this view
# TODO: Add login required once user group login achieved make another page for signup - dashboard
def home(request: HttpRequest) -> HttpResponse:
    """View to serve home page template"""

    # TODO: handle empty database state
    w_sum = Water.objects.aggregate(Sum("quantity"))["quantity__sum"]
    w_price = 40 * (w_sum if w_sum else 0)
    w_pp = w_price / 4

    # TODO: handle empty database state
    electricity = None
    try:
        electricity = Electricity.objects.latest("due_date")
        e_pp = electricity.price / 4
        # TODO: add this filed as model property
        e_days_left = (electricity.due_date - timezone.now().date()).days
    except ObjectDoesNotExist:
        e_pp, e_days_left = 0, 0

    # TODO: handle empty database state
    maid = None
    try:
        maid = Maid.objects.latest("due_date")
        m_pp = maid.price / 4
        # TODO: add this filed as model property
        m_days_left = (maid.due_date - timezone.now().date()).days
    except ObjectDoesNotExist:
        m_pp, m_days_left = 0, 0

    # TODO: remove hardcoded group name
    users = User.objects.filter(groups__name="d52")

    # TODO: review and optimize this logic
    records = []
    for user in users:
        total_spent = Record.objects.filter(purchaser=user).aggregate(Sum("price"))[
            "price__sum"
        ]
        records.append({"user": user, "total_spent": total_spent})

    context = {
        "home_active": "active",
        "records": records,
        "w_sum": w_sum,
        "w_price": w_price,
        "w_pp": w_pp,
        "electricity": electricity,
        "e_pp": e_pp,
        "e_days_left": e_days_left,
        "maid": maid,
        "m_pp": m_pp,
        "m_days_left": m_days_left,
    }

    # TODO: #19 fix ui for single user
    return render(request, "core/index.html", context)


# TODO: Update wording and doc for view template
class AboutTemplateView(TemplateView):
    """View to render the about page template."""

    template_name = "core/about.html"
    extra_context = {"about_active": "active"}


class FeedbackCreateView(SuccessMessageMixin, CreateView):
    """View  to handle the creation of user feedback"""

    form_class = FeedbackFrom
    success_url = reverse_lazy("core:home")
    template_name = "core/feedback.html"
    success_message = "Thank you for your valuable feedback, it will help us to improve your experience."
    extra_context = {"feedback_active": "active"}
