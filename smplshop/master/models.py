from django.db import models


# Create your models here.
class Store(models.Model):
    code = models.CharField(
        max_length=15, verbose_name="Store Code", blank=False, unique=True
    )
    name = models.CharField(
        max_length=30, verbose_name="Store Name", blank=False, unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("code", "name")
