from django.db.models import Q
from django.forms import ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Product, Store


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
