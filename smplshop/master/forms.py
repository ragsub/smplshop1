from django.db.models import Q
from django.forms import ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _

from smplshop.customforms.widgets import DatalistWidget

from .models import Product, ProductInStore, Store


class AddStoreForm(ModelForm):
    class Meta:
        model = Store
        fields = ["code", "name"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        if self.Meta.model.objects.filter(Q(name__iexact=name)).exists():
            raise ValidationError(
                _("%(value)s is already a store name"),
                params={"value": name},
                code="duplicate_name",
            )

        return name

    def clean_code(self):
        code = self.cleaned_data["code"]

        if self.Meta.model.objects.filter(Q(code__iexact=code)).exists():
            raise ValidationError(
                _("%(value)s is already a store code"),
                params={"value": code},
                code="duplicate_code",
            )

        return code


class AddProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["code", "name"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        if self.Meta.model.objects.filter(Q(name__iexact=name)).exists():
            raise ValidationError(
                _("%(value)s is already a product name"),
                params={"value": name},
                code="duplicate_name",
            )

        return name

    def clean_code(self):
        code = self.cleaned_data["code"]

        if self.Meta.model.objects.filter(Q(code__iexact=code)).exists():
            raise ValidationError(
                _("%(value)s is already a product code"),
                params={"value": code},
                code="duplicate_code",
            )

        return code


class AddProductInStoreForm(ModelForm):
    # options = list(Product.objects.all().values_list("name", "code"))

    # product = TypedChoiceField(choices=options, widget=DatalistWidget())

    class Meta:
        model = ProductInStore
        fields = ["store", "product", "price"]
        widgets = {"product": DatalistWidget()}

    def clean_product(self):
        product = self.cleaned_data["product"]
        if not Product.objects.filter(name=product).exists():
            raise ValidationError(
                _("%(product)s is not a valid product"),
                params={"product": product},
                code="invalid_product",
            )
        else:
            product = Product.objects.get(name=product)
        return product
