# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20161127_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='tfidf',
            field=models.CharField(default='', max_length=5000),
        ),
    ]
