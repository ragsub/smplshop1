from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Store(models.Model):
    code = models.CharField(
        max_length=15,
        verbose_name="Store Code",
        blank=False,
        unique=True,
        validators=[
            RegexValidator(
                r"^[A-Za-z0-9_]+$",
                _("Store code can only be alphanumeric or underscore"),
            )
        ],
    )
    name = models.CharField(
        max_length=40, verbose_name="Store Name", blank=False, unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("code", "name")
