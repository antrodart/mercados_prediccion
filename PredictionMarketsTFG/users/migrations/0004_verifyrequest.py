# Generated by Django 2.1.7 on 2019-07-23 18:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20190723_1817'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerifyRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=60)),
                ('biography', models.TextField()),
                ('is_accepted', models.BooleanField(default=None, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
