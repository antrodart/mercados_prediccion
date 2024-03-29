# Generated by Django 2.1.7 on 2019-06-18 08:21

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('is_yes', models.BooleanField(default=True)),
                ('has_expired', models.BooleanField(default=False)),
                ('is_judged', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=140, verbose_name='Title in English')),
                ('title_es', models.CharField(max_length=140, verbose_name='Title in Spanish')),
                ('picture', models.TextField(verbose_name='Picture')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('rating', models.IntegerField(default=0)),
                ('moment', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
                ('description', models.TextField()),
                ('picture', models.TextField(blank=True, null=True, verbose_name='Picture')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('is_visible', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='JoinedCommunity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_karma', models.IntegerField(default=0)),
                ('joined_date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True)),
                ('is_accepted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('end_date', models.DateField()),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('picture', models.TextField()),
                ('is_judged', models.BooleanField(default=False)),
                ('is_binary', models.BooleanField(default=True)),
                ('categories', models.ManyToManyField(to='mercados_de_prediccion.Category')),
                ('community', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mercados_de_prediccion.Community')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('is_correct', models.BooleanField(default=False, null=True)),
                ('binary_yes', models.BooleanField(default=None, null=True)),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mercados_de_prediccion.Market')),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buy_price', models.IntegerField(default=50, validators=[django.core.validators.MaxValueValidator(99), django.core.validators.MinValueValidator(1)])),
                ('date', models.DateField(auto_now_add=True)),
                ('is_yes', models.BooleanField()),
                ('is_last', models.BooleanField(default=True)),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mercados_de_prediccion.Option')),
            ],
        ),
    ]
