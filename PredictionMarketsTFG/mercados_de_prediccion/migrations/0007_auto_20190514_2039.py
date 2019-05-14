# Generated by Django 2.1.7 on 2019-05-14 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercados_de_prediccion', '0006_group_creation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_visible',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='market',
            name='title',
            field=models.CharField(max_length=150),
        ),
    ]