# Generated by Django 4.0 on 2022-10-10 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0005_alter_store_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(max_length=40, unique=True, verbose_name='Store Name'),
        ),
    ]
