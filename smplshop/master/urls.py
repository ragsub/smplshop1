from django.urls import path

from smplshop.master.views import (
    ProductCreateView,
    ProductListView,
    StoreCreateView,
    StoreListView,
)

app_name = "smplshop.master"
urlpatterns = [
    path("store/", view=StoreListView.as_view(), name="store_list"),
    path("store/add/", view=StoreCreateView.as_view(), name="store_add"),
    path("product/", view=ProductListView.as_view(), name="product_list"),
    path("product/add/", view=ProductCreateView.as_view(), name="product_add"),
]
