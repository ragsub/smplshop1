from django.urls import path

from smplshop.transaction.views import StoreOrderListView, change_order_status

app_name = "smplshop.transaction"
urlpatterns = [
    path("orders/", view=StoreOrderListView.as_view(), name="orders"),
    path("order/status", view=change_order_status, name="change_order_status"),
]
