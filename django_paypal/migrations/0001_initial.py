# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaypalItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sku', models.CharField(max_length=127, verbose_name='stock keeping unit')),
                ('name', models.CharField(max_length=127, verbose_name='name')),
                ('description', models.CharField(max_length=127, verbose_name='description', blank=True)),
                ('quantity', models.CharField(max_length=10, verbose_name='quantity')),
                ('price', models.CharField(max_length=10, verbose_name='price')),
                ('currency', models.CharField(max_length=3, verbose_name='currency')),
                ('tax', models.CharField(max_length=10, verbose_name='currency', blank=True)),
                ('url', models.URLField(verbose_name='url', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
            ],
            options={
                'verbose_name': 'Paypal Item',
                'verbose_name_plural': 'Paypal Item',
            },
        ),
        migrations.CreateModel(
            name='PaypalPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_id', models.CharField(unique=True, max_length=255, verbose_name='payment id')),
                ('intent', models.CharField(max_length=255, verbose_name='intent')),
                ('experience_profile_id', models.CharField(max_length=255, verbose_name='intent', blank=True)),
                ('note_to_payer', models.CharField(max_length=165, verbose_name='intent', blank=True)),
                ('state', models.CharField(max_length=255, verbose_name='state', blank=True)),
                ('payment_method', models.CharField(max_length=255, verbose_name='payment method')),
                ('custom', models.CharField(max_length=255, verbose_name='payment method')),
                ('payer_id', models.CharField(max_length=255, verbose_name='payer id')),
                ('failure_reason', models.CharField(max_length=255, verbose_name='failure reason', blank=True)),
                ('link', models.URLField(verbose_name='link')),
                ('approve_link', models.URLField(verbose_name='approve link')),
                ('execute_link', models.URLField(verbose_name='execute link', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
            ],
            options={
                'verbose_name': 'Paypal Payment',
                'verbose_name_plural': 'Paypal Payments',
            },
        ),
        migrations.CreateModel(
            name='PaypalTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_amount', models.DecimalField(verbose_name='total amount', max_digits=9, decimal_places=2)),
                ('currency', models.CharField(max_length=10, verbose_name='currency')),
                ('subtotal', models.DecimalField(verbose_name='subtotal', max_digits=9, decimal_places=2)),
                ('tax', models.DecimalField(verbose_name='tax', max_digits=9, decimal_places=2, blank=True)),
                ('shipping', models.DecimalField(verbose_name='shipping', max_digits=9, decimal_places=2, blank=True)),
                ('handling_fee', models.DecimalField(verbose_name='handling fee', max_digits=9, decimal_places=2, blank=True)),
                ('shipping_discount', models.DecimalField(verbose_name='shipping discount', max_digits=9, decimal_places=2, blank=True)),
                ('insurance', models.DecimalField(verbose_name='insurance fee', max_digits=9, decimal_places=2, blank=True)),
                ('gift_wrap', models.DecimalField(verbose_name='gift wrap fee', max_digits=9, decimal_places=2, blank=True)),
                ('reference_id', models.CharField(max_length=255, verbose_name='reference id', blank=True)),
                ('settlement_destination', models.CharField(default='PARTNER_BALANCE', max_length=255, verbose_name='settlement destination')),
                ('allowed_payment_method', models.CharField(default='INSTANT_FUNDING_SOURCE', max_length=255, verbose_name='allowed payment method')),
                ('description', models.CharField(max_length=255, verbose_name='description', blank=True)),
                ('note_to_payee', models.CharField(max_length=255, verbose_name='note to payee', blank=True)),
                ('custom', models.CharField(max_length=127, verbose_name='custom', blank=True)),
                ('invoice_number', models.CharField(max_length=127, verbose_name='invoice number')),
                ('purchase_order', models.CharField(max_length=127, verbose_name='purchase order')),
                ('soft_descriptor', models.CharField(max_length=22, verbose_name='soft descriptor')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('shipping_method', models.CharField(max_length=255, verbose_name='shipping method', blank=True)),
                ('shipping_phone_number', models.CharField(max_length=255, verbose_name='shipping phone number', blank=True)),
                ('shipping_address_line_1', models.CharField(max_length=100, verbose_name='shipping address line 1')),
                ('shipping_address_line_2', models.CharField(max_length=100, verbose_name='shipping address line 2', blank=True)),
                ('shipping_address_city', models.CharField(max_length=50, verbose_name='shipping address city')),
                ('shipping_address_country', models.CharField(max_length=2, verbose_name='shipping address country')),
                ('shipping_address_postal_code', models.CharField(max_length=20, verbose_name='shipping address postal code', blank=True)),
                ('shipping_address_state', models.CharField(max_length=100, verbose_name='shipping address state', blank=True)),
                ('shipping_address_phone', models.CharField(max_length=50, verbose_name='shipping address phone')),
                ('shipping_address_normalization_status', models.CharField(default='UNKNOWN', max_length=50, verbose_name='shipping address normalization status')),
                ('shipping_address_type', models.CharField(default='HOME_OR_WORK', max_length=50, verbose_name='shipping address type')),
                ('shipping_address_recipient_name', models.CharField(max_length=127, verbose_name='shipping address recipient name')),
                ('payment', models.ForeignKey(related_name='transactions', verbose_name='payment', to='django_paypal.PaypalPayment', on_delete=models.deletion.PROTECT)),
            ],
            options={
                'verbose_name': 'Paypal Transaction',
                'verbose_name_plural': 'Paypal Transactions',
            },
        ),
        migrations.AddField(
            model_name='paypalitem',
            name='transaction',
            field=models.ForeignKey(related_name='items', verbose_name='transaction', to='django_paypal.PaypalTransaction', on_delete=models.deletion.PROTECT),
        ),
    ]
