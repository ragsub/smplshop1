# Generated by Django 4.0 on 2022-10-25 11:37

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('master', '0004_alter_productinstore_options'),
        ('shop', '0003_cartitem_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='price',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='product',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product_in_store',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='master.productinstore', verbose_name='Product In Store'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Quanity'),
        ),
    ]