# Generated by Django 2.1.7 on 2019-06-04 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercados_de_prediccion', '0013_auto_20190604_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='is_last',
            field=models.BooleanField(default=True),
        ),
    ]