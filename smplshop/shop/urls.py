from django.urls import path

from smplshop.shop.views import (
    CartView,
    OrderListView,
    ShopFrontView,
    add_to_cart,
    place_order,
)

app_name = "smplshop.shop"
urlpatterns = [
    path("<str:shop>/", view=ShopFrontView.as_view(), name="shop_front"),
    path(
        "<str:shop>/cart/add/<uuid:product_in_store_uuid>/",
        view=add_to_cart,
        name="add_to_cart",
    ),
    path("<str:shop>/cart/", view=CartView.as_view(), name="cart"),
    path("<str:shop>/cart/order/", view=place_order, name="place_order"),
    path("<str:shop>/orders/", view=OrderListView.as_view(), name="customer_orders"),
]
