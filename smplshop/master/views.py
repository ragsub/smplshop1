from django.db.models.base import ModelBase

from smplshop.genericview.views import GenericCreateView, GenericListView

from .forms import AddProductForm, AddProductInStoreForm, AddStoreForm
from .models import Product, ProductInStore, Store


# Create your views here.
class StoreListView(GenericListView):
    model: ModelBase = Store
    fields = ["code", "name"]
    template_name = "master/store_list.html"
    attribute = "code"


class StoreCreateView(GenericCreateView):
    model = Store
    form_class = AddStoreForm
    success_message = "%(name)s store added successfully"
    success_view_name = "smplshop.master:store_list"
    attribute = "code"


class ProductListView(GenericListView):
    model = Product
    fields = ["code", "name"]
    template_name = "master/product_list.html"
    attribute = "code"


class ProductCreateView(GenericCreateView):
    model = Product
    form_class = AddProductForm
    success_message = "%(name)s product added successfully"
    success_view_name = "smplshop.master:product_list"
    attribute = "code"


class ProductInStoreListView(GenericListView):
    model = ProductInStore
    fields = ["store", "product", "price"]
    template_name = "master/product_in_store_list.html"
    attribute = "uuid"


class ProductInStoreCreateView(GenericCreateView):
    model = ProductInStore
    form_class = AddProductInStoreForm
    success_message = "%(product)s in %(store)s added successfully"
    success_view_name = "smplshop.master:product_in_store_list"
    attribute = "uuid"
    template_name = "master/product_in_store_add.html"
