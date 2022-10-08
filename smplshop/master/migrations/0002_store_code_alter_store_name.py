# Generated by Django 4.0 on 2022-10-08 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='code',
            field=models.CharField(default='deddd', max_length=10, unique=True, verbose_name='Store Code'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(max_length=20, unique=True, verbose_name='Store Name'),
        ),
    ]