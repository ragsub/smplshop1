from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from smplshop.master.models import Store
from smplshop.shop.models import Order


class StoreOrderListView(LoginRequiredMixin, ListView):
    model = Store
    template_name: str = "transaction/orders.html"

    def get_queryset(self) -> QuerySet[Any]:

        qs = super().get_queryset().prefetch_related("order_set")

        return qs


@login_required
def change_order_status(request: HttpRequest):
    order_uuid = request.GET.get("order_uuid", None)
    status_change = request.GET.get("change_status", None)
    if (order_uuid is None) | (status_change is None):
        messages.error(request, "Order id and change_status has to be filled")
        return redirect(reverse("smplshop.transaction:orders"))

    order = get_object_or_404(Order, uuid=order_uuid)

    try:
        if status_change == "accept":
            order.accept_order()
            messages.success(
                request,
                "{}{}{}".format("Status of order ", order_uuid, " updated to accepted"),
            )

        elif status_change == "ship":
            order.ship_order()
            messages.success(
                request,
                "{}{}{}".format("Status of order ", order_uuid, " updated to shipped"),
            )

        elif status_change == "deliver":
            order.deliver_order()
            messages.success(
                request,
                "{}{}{}".format(
                    "Status of order ", order_uuid, " updated to delivered"
                ),
            )

        elif status_change == "close":
            order.close_order()
            messages.success(
                request,
                "{}{}{}".format("Status of order ", order_uuid, " updated to closed"),
            )

        elif status_change == "cancel":
            order.cancel_order()
            messages.success(
                request,
                "{}{}{}".format(
                    "Status of order ", order_uuid, " updated to cancelled"
                ),
            )

        else:
            messages.error(
                request,
                "{}{}{}".format("Status ", status_change, " is not an allowed value"),
            )
    except ValidationError as e:
        messages.error(request, e.args[0])

    return redirect(reverse("smplshop.transaction:orders"))
