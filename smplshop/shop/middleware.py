from django.http import HttpResponseNotFound
from django.http.request import HttpRequest

from smplshop.master.models import Store


class GetShopMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        path_components = request.path.split("/")

        if path_components[1] == "shop":
            if Store.objects.filter(code=path_components[2]).exists():
                request.shop = Store.objects.get(code=path_components[2])  # type: ignore
            else:
                return HttpResponseNotFound(
                    "Shop %s does not exist" % (path_components[2])
                )
