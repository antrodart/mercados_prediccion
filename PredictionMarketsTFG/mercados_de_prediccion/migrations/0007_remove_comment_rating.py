# Generated by Django 2.1.7 on 2019-08-20 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mercados_de_prediccion', '0006_market_judgement_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='rating',
        ),
    ]