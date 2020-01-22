# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_paypal', '0002_auto_20171002_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='paypalpayment',
            name='related_resource_id',
            field=models.CharField(blank=True, max_length=255, verbose_name='related resource id'),
        ),
    ]
