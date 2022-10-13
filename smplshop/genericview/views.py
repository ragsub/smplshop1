import math
from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Case, Q, Value, When
from django.db.models.base import ModelBase
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView


# Create your views here.
class GenericListView(LoginRequiredMixin, ListView):
    model: ModelBase
    fields: list
    paginate_by: int = settings.ITEMS_PER_PAGE
    template_name: str

    def get_verbose_field_name(self, field: str):
        return self.model._meta.get_field(field).verbose_name  # type: ignore

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["model"] = self.model
        context["fields"] = []
        for field in self.fields:
            context["fields"].append(self.get_verbose_field_name(field))
        context["fields"].append("Changed")

        new_code = self.request.GET.get("new_code", None)
        if new_code is not None and self.paginate_by is not None:
            obj = get_object_or_404(self.model, code=new_code)  # type: ignore
            if obj:
                new_page = math.floor(self.get_page(obj.id))  # type: ignore
                context["page_obj"] = context["paginator"].page(new_page)
                context["object_list"] = (
                    context["paginator"]
                    .page(new_page)
                    .object_list.annotate(
                        new=Case(
                            When(id=obj.id, then=Value("New")),
                            When(~Q(id=obj.id), then=Value("")),  # type: ignore
                        )
                    )
                )

        return context

    def get_page(self, id):
        return (
            list(self.get_queryset().values_list("id", flat=True)).index(id)
            / self.paginate_by
        ) + 1

    def get_queryset(self):
        return super().get_queryset().values_list(*self.fields).annotate(new=Value(""))


class GenericCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model: ModelBase
    fields: list
    template_name: str = "genericview/add.html"
    success_message: str
    success_view_name: str

    def get_success_url(self) -> str:
        success_url = (
            reverse_lazy(self.success_view_name)
            + "?new_code="
            + str(self.object.code)  # type: ignore
        )
        return success_url

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_invalid(form)
        response.status_code = 400
        return response
