from typing import Any

from django.forms.widgets import Select


class DatalistWidget(Select):
    input_type = "text"
    template_name = "customforms/widgets/datalist.html"
    option_template_name = "customforms/widgets/datalist_option.html"
    add_id_index = False
    checked_attribute = {"selected": True}
    option_inherits_attrs = False

    def get_context(self, name: str, value: Any, attrs) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        context["widget"]["type"] = "text"
        context["widget"]["data"] = "data_list"
        return context
