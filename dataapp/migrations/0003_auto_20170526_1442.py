# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-26 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dataapp', '0002_auto_20170525_1220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inverseindex',
            name='index',
        ),
        migrations.AddField(
            model_name='inverseindex',
            name='index',
            field=models.CharField(default='foo', max_length=100),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Provenance',
        ),
    ]
