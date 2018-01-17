# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_paypal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paypalpayment',
            name='approve_link',
            field=models.URLField(verbose_name='approve link', blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpayment',
            name='custom',
            field=models.CharField(max_length=255, verbose_name='payment method', blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpayment',
            name='link',
            field=models.URLField(verbose_name='link', blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpayment',
            name='payer_id',
            field=models.CharField(max_length=255, verbose_name='payer id', blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpayment',
            name='payment_method',
            field=models.CharField(max_length=255, verbose_name='payment method', blank=True),
        ),
        migrations.AddField(
            model_name='paypalpayment',
            name='transaction_fee',
            field=models.DecimalField(default=Decimal('0'), verbose_name='transaction fee', max_digits=9, decimal_places=2),
        ),
    ]
