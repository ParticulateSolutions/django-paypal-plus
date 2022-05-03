from __future__ import unicode_literals

import json
import logging

from decimal import Decimal
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _


@python_2_unicode_compatible
class PaypalPayment(models.Model):
    payment_id = models.CharField(_("payment id"), max_length=255, unique=True)  # id created by paypal
    intent = models.CharField(_("intent"), max_length=255)  # sale
    experience_profile_id = models.CharField(_("intent"), max_length=255, blank=True)  # sale
    note_to_payer = models.CharField(_("intent"), max_length=165, blank=True)  # sale
    state = models.CharField(_("state"), max_length=255, blank=True)
    payment_method = models.CharField(_("payment method"), max_length=255, blank=True)
    custom = models.CharField(_("payment method"), max_length=255, blank=True)
    payer_id = models.CharField(_("payer id"), max_length=255, blank=True)
    transaction_fee = models.DecimalField(_("transaction fee"), max_digits=9, decimal_places=2, default=Decimal(0))
    related_resource_id = models.CharField(_("related resource id"), max_length=255, blank=True, null=True)
    initial_response_object = models.TextField(_("initial post response"), null=True, blank=True)
    update_response_object = models.TextField(_("updated get response"), null=True, blank=True)

    failure_reason = models.CharField(_("failure reason"), max_length=255, blank=True)

    link = models.URLField(_("link"), blank=True)
    approve_link = models.URLField(_("approve link"), blank=True)
    execute_link = models.URLField(_("execute link"), blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.payment_id

    class Meta:
        verbose_name = _("Paypal Payment")
        verbose_name_plural = _("Paypal Payments")

    def execute(self, paypal_wrapper):
        if not self.execute_link:
            return False
        if self.state == 'approved':
            return False
        if not self.payer_id:
            return False
        execute_response = paypal_wrapper.call_api(url=self.execute_link, data={'payer_id': self.payer_id})
        if execute_response and 'state' in execute_response and execute_response['state'] == 'approved':
            self.state = 'approved'
            self.save()
            return True
        return False

    def refresh_from_paypal(self, paypal_wrapper, expected_status=None):
        payment_response = paypal_wrapper.call_api(url=self.link)
        if not payment_response:
            logger = logging.getLogger(__name__)
            logger.error("Paypal Payment Link not available: {}".format(self.link))
            return False

        if expected_status and expected_status != payment_response['state']:
            logger = logging.getLogger(__name__)
            logger.error("Paypal Payment Status Error: expected: {0}, found: {1}".format(expected_status, payment_response['state']))
            return False

        self.update_response_object = json.dumps(payment_response)

        if payment_response['state'] == 'approved':
            fee = Decimal(0)
            for transaction in payment_response['transactions']:
                if 'related_resources' in transaction:
                    for resource in transaction['related_resources']:
                        if 'sale' in resource:
                            if 'links' in resource['sale']:
                                for link in resource['sale']['links']:
                                    if 'rel' in link and link['rel'] == 'self':
                                        sale_response = paypal_wrapper.call_api(url=link['href'])
                                        if sale_response and 'transaction_fee' in sale_response and 'value' in sale_response['transaction_fee'] and sale_response['transaction_fee']['currency'] == 'EUR':
                                            self.transaction_fee = Decimal(sale_response['transaction_fee']['value'])
                            if 'id' in resource['sale']:
                                self.related_resource_id = resource['sale']['id']

        if 'payer' in payment_response and 'payer_info' in payment_response['payer'] and 'payer_id' in payment_response['payer']['payer_info']:
            self.payer_id = payment_response['payer']['payer_info']['payer_id']

        if 'failure_reason' in payment_response:
            self.failure_reason = payment_response['failure_reason']

        self.state = payment_response['state']

        if 'links' in payment_response:
            for link in payment_response['links']:
                if 'rel' in link:
                    if link['rel'] == "self":
                        self.link = link['href']
                    elif link['rel'] == "approval_url":
                        self.approve_link = link['href']
                    elif link['rel'] == "execute":
                        self.execute_link = link['href']
        self.save()

        return self


@python_2_unicode_compatible
class PaypalTransaction(models.Model):
    payment = models.ForeignKey(PaypalPayment, verbose_name=_("payment"), related_name='transactions', on_delete=models.PROTECT)

    total_amount = models.DecimalField(_("total amount"), max_digits=9, decimal_places=2)
    currency = models.CharField(_("currency"), max_length=10)
    subtotal = models.DecimalField(_("subtotal"), max_digits=9, decimal_places=2)
    tax = models.DecimalField(_("tax"), max_digits=9, decimal_places=2, blank=True)
    shipping = models.DecimalField(_("shipping"), max_digits=9, decimal_places=2, blank=True)
    handling_fee = models.DecimalField(_("handling fee"), max_digits=9, decimal_places=2, blank=True)
    shipping_discount = models.DecimalField(_("shipping discount"), max_digits=9, decimal_places=2, blank=True)
    insurance = models.DecimalField(_("insurance fee"), max_digits=9, decimal_places=2, blank=True)
    gift_wrap = models.DecimalField(_("gift wrap fee"), max_digits=9, decimal_places=2, blank=True)

    reference_id = models.CharField(_("reference id"), max_length=255, blank=True)
    settlement_destination = models.CharField(_("settlement destination"), max_length=255, default="PARTNER_BALANCE")
    allowed_payment_method = models.CharField(_("allowed payment method"), max_length=255, default="INSTANT_FUNDING_SOURCE")  # UNRESTRICTED or INSTANT_FUNDING_SOURCE or IMMEDIATE_PAY
    description = models.CharField(_("description"), max_length=255, blank=True)
    note_to_payee = models.CharField(_("note to payee"), max_length=255, blank=True)
    custom = models.CharField(_("custom"), max_length=127, blank=True)
    invoice_number = models.CharField(_("invoice number"), max_length=127)
    purchase_order = models.CharField(_("purchase order"), max_length=127)
    soft_descriptor = models.CharField(_("soft descriptor"), max_length=22)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    shipping_method = models.CharField(_("shipping method"), max_length=255, blank=True)
    shipping_phone_number = models.CharField(_("shipping phone number"), max_length=255, blank=True)

    shipping_address_line_1 = models.CharField(_("shipping address line 1"), max_length=100)  # number, street, etc.
    shipping_address_line_2 = models.CharField(_("shipping address line 2"), max_length=100, blank=True)  # apt number, etc.
    shipping_address_city = models.CharField(_("shipping address city"), max_length=50)
    shipping_address_country = models.CharField(_("shipping address country"), max_length=2)
    shipping_address_postal_code = models.CharField(_("shipping address postal code"), max_length=20, blank=True)  # required in certain countries
    shipping_address_state = models.CharField(_("shipping address state"), max_length=100, blank=True)
    shipping_address_phone = models.CharField(_("shipping address phone"), max_length=50)
    shipping_address_normalization_status = models.CharField(_("shipping address normalization status"), max_length=50, default="UNKNOWN")  # UNKNOWN or UNNORMALIZED_USER_PREFERRED or NORMALIZED or UNNORMALIZED
    shipping_address_type = models.CharField(_("shipping address type"), max_length=50, default="HOME_OR_WORK")  # HOME_OR_WORK or GIFT or other
    shipping_address_recipient_name = models.CharField(_("shipping address recipient name"), max_length=127)

    objects = models.Manager()

    def __str__(self):
        return '{} - {} {}'.format(self.reference_id, self.total_amount, self.currency)

    class Meta:
        verbose_name = _("Paypal Transaction")
        verbose_name_plural = _("Paypal Transactions")


@python_2_unicode_compatible
class PaypalItem(models.Model):
    transaction = models.ForeignKey(PaypalTransaction, verbose_name=_("transaction"), related_name='items', on_delete=models.PROTECT)

    sku = models.CharField(_("stock keeping unit"), max_length=127)
    name = models.CharField(_("name"), max_length=127)
    description = models.CharField(_("description"), max_length=127, blank=True)
    quantity = models.CharField(_("quantity"), max_length=10)
    price = models.CharField(_("price"), max_length=10)
    currency = models.CharField(_("currency"), max_length=3)
    tax = models.CharField(_("currency"), max_length=10, blank=True)
    url = models.URLField(_("url"), blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Paypal Item")
        verbose_name_plural = _("Paypal Item")
