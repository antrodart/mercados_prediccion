# Generated by Django 2.1.7 on 2019-05-28 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercados_de_prediccion', '0009_auto_20190522_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='is_yes',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='option',
            name='name',
            field=models.CharField(max_length=40),
        ),
    ]