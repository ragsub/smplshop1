from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .models import Store


# Create your views here.
class StoreListView(LoginRequiredMixin, ListView):
    model = Store
    fields = ["code", "name"]
    paginate_by: int = settings.ITEMS_PER_PAGE
    template_name = "master/store_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model"] = self.model
        context["fields"] = self.fields
        return context

    def get_queryset(self):
        return super().get_queryset().values_list(*self.fields)


class StoreCreateView(CreateView):
    model = Store
    fields = ["code", "name"]
    template_name: str = "master/add.html"
    success_url = reverse_lazy("smplshop.master:store_list")
