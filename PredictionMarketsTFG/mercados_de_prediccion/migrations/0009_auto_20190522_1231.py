# Generated by Django 2.1.7 on 2019-05-22 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mercados_de_prediccion', '0008_auto_20190522_1150'),
    ]

    operations = [
        migrations.RenameField(
            model_name='market',
            old_name='category',
            new_name='categories',
        ),
    ]
