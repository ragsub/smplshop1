# Generated by Django 4.0 on 2022-10-08 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0002_store_code_alter_store_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(max_length=30, unique=True, verbose_name='Store Name'),
        ),
    ]