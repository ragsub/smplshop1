from django.urls import path

from smplshop.master.views import StoreCreateView, StoreListView

app_name = "smplshop.master"
urlpatterns = [
    path("store/", view=StoreListView.as_view(), name="store_list"),
    path("store/add/", view=StoreCreateView.as_view(), name="store_add"),
]
