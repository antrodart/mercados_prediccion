# Generated by Django 2.1.7 on 2019-05-20 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercados_de_prediccion', '0005_asset_market'),
    ]

    operations = [
        migrations.AddField(
            model_name='market',
            name='is_binary',
            field=models.BooleanField(default=True),
        ),
    ]