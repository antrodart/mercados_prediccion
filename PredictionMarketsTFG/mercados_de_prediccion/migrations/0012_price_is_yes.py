# Generated by Django 2.1.7 on 2019-06-01 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercados_de_prediccion', '0011_auto_20190601_1951'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='is_yes',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]