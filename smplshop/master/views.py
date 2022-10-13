from django.db.models.base import ModelBase

from smplshop.genericview.views import GenericCreateView, GenericListView

from .forms import AddProductForm, AddStoreForm
from .models import Product, Store


# Create your views here.
class StoreListView(GenericListView):
    model: ModelBase = Store
    fields = ["code", "name"]
    template_name = "master/store_list.html"


class StoreCreateView(GenericCreateView):
    model = Store
    form_class = AddStoreForm
    success_message = "%(name)s store added successfully"
    success_view_name = "smplshop.master:store_list"


class ProductListView(GenericListView):
    model = Product
    fields = ["code", "name"]
    template_name = "master/product_list.html"


class ProductCreateView(GenericCreateView):
    model = Product
    form_class = AddProductForm
    success_message = "%(name)s product added successfully"
    success_view_name = "smplshop.master:product_list"
