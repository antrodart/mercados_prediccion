# Generated by Django 2.1.7 on 2019-05-14 08:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercados_de_prediccion', '0005_market_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2019, 5, 14, 10, 56, 38, 934912)),
            preserve_default=False,
        ),
    ]
