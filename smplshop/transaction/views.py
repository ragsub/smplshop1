from typing import Any

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from smplshop.master.models import Store
from smplshop.shop.models import Order


class StoreOrderListView(ListView):
    model = Store
    template_name: str = "transaction/orders.html"

    def get_queryset(self) -> QuerySet[Any]:

        qs = super().get_queryset().prefetch_related("order_set")

        return qs


def change_order_status(request: HttpRequest):
    order_uuid = request.GET.get("order_uuid", None)
    status_change = request.GET.get("change_status", None)
    if (order_uuid is None) | (status_change is None):
        messages.error(
            request, "Order id and statusstatus_change change has to be filled"
        )
        return redirect(reverse("smplshop.transaction:orders"))

    order = get_object_or_404(Order, uuid=order_uuid)

    if status_change == "accept":
        order.accept_order()
    elif status_change == "ship":
        order.ship_order()
    elif status_change == "deliver":
        order.deliver_order()
    elif status_change == "close":
        order.close_order()
    elif status_change == "cancel":
        order.cancel_order()
    else:
        messages.error(request, "Status is not an allowed value")

    return redirect(reverse("smplshop.transaction:orders"))
