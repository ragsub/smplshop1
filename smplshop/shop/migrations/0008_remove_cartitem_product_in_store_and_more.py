# Generated by Django 4.0 on 2022-10-25 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("master", "0004_alter_productinstore_options"),
        ("shop", "0007_remove_cartitem_product_in_store_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cartitem",
            name="product_in_store",
        ),
        migrations.AddField(
            model_name="cartitem",
            name="product_in_store",
            field=models.ForeignKey(
                default=16,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cart_items",
                to="master.productinstore",
                verbose_name="Product In Store",
            ),
            preserve_default=False,
        ),
    ]
