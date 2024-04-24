from __future__ import unicode_literals


from decimal import Decimal
from typing import List

from dataclass_wizard import fromdict
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_paypal.api_types import Capture

try:
    # Django 3.1 and newer
    from django.db.models import JSONField
except ImportError:
    # Django 2.2
    from django.contrib.postgres.fields import JSONField


class PaypalOrder(models.Model):
    order_id = models.CharField(_('Order ID'), max_length=255, unique=True)
    status = models.CharField(_('Status'), max_length=255, blank=True)

    def get_capture_api_responses(self) -> models.QuerySet:
        return self.api_responses.filter(url__contains=f'/v2/checkout/orders/{self.order_id}/capture')

    @property
    def captures(self) -> List[Capture]:
        captures: List[Capture] = list()
        for capture_response in self.get_capture_api_responses():
            for purchase_unit in capture_response.response_data.get('purchase_units', []):
                for capture in purchase_unit.get('payments', {}).get('captures', []):
                    captures.append(fromdict(Capture, capture))
        return captures


class PaypalAPIPostData(models.Model):
    order = models.ForeignKey(PaypalOrder, related_name='api_posts', on_delete=models.CASCADE)
    url = models.CharField(_('URL'), max_length=255, blank=True)
    post_data = JSONField(_('Post Data'))
    created_at = models.DateTimeField(auto_now_add=True)


class PaypalAPIResponse(models.Model):
    order = models.ForeignKey(PaypalOrder, related_name='api_responses', on_delete=models.CASCADE)
    post = models.ForeignKey(PaypalAPIPostData, related_name='responses', null=True, on_delete=models.CASCADE)
    url = models.CharField(_('URL'), max_length=255, blank=True)
    response_data = JSONField(_('Response Data'))
    created_at = models.DateTimeField(auto_now_add=True)


class PaypalWebhook(models.Model):
    webhook_id = models.CharField(_('Webhook ID'), max_length=255, unique=True)
    auth_hash = models.CharField(_('Auth Hash'), max_length=255, default='')
    url = models.CharField('URL', max_length=255)
    event_types = JSONField(_('Active Webhook Events'))

    class Meta:
        unique_together = (
            'url',
            'auth_hash',
        )


class PaypalWebhookEvent(models.Model):
    payload = JSONField(_('Payload'))
    order = models.ForeignKey(PaypalOrder, related_name='webhook_events', on_delete=models.CASCADE)
    webhook = models.ForeignKey(PaypalWebhook, related_name='events', on_delete=models.CASCADE)


# The following models solely exist to keep payments made in version <0.3.0 stored in the database.
# They are not used in the current version of the app and have been created using /v1/payments.
# They might get removed in a future version.
class LegacyPaypalPayment(models.Model):
    payment_id = models.CharField(_('payment id'), max_length=255, unique=True)  # id created by paypal
    intent = models.CharField(_('intent'), max_length=255)  # sale
    experience_profile_id = models.CharField(_('intent'), max_length=255, blank=True)  # sale
    note_to_payer = models.CharField(_('intent'), max_length=165, blank=True)  # sale
    state = models.CharField(_('state'), max_length=255, blank=True)
    payment_method = models.CharField(_('payment method'), max_length=255, blank=True)
    custom = models.CharField(_('payment method'), max_length=255, blank=True)
    payer_id = models.CharField(_('payer id'), max_length=255, blank=True)
    transaction_fee = models.DecimalField(_('transaction fee'), max_digits=9, decimal_places=2, default=Decimal(0))
    related_resource_id = models.CharField(_('related resource id'), max_length=255, blank=True, null=True)
    related_resource_state = models.CharField(_('related resource state'), max_length=255, blank=True, null=True)
    initial_response_object = models.TextField(_('initial post response'), null=True, blank=True)
    update_response_object = models.TextField(_('updated get response'), null=True, blank=True)

    failure_reason = models.CharField(_('failure reason'), max_length=255, blank=True)

    link = models.URLField(_('link'), blank=True)
    approve_link = models.URLField(_('approve link'), blank=True)
    execute_link = models.URLField(_('execute link'), blank=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    last_modified = models.DateTimeField(_('last modified'), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.payment_id

    class Meta:
        verbose_name = _('Legacy Paypal Payment (payments v1 API)')
        verbose_name_plural = _('Legacy Paypal Payments (payments v1 API)')


class LegacyPaypalTransaction(models.Model):
    payment = models.ForeignKey(LegacyPaypalPayment, verbose_name=_('payment'), related_name='transactions', on_delete=models.PROTECT)

    total_amount = models.DecimalField(_('total amount'), max_digits=9, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=10)
    subtotal = models.DecimalField(_('subtotal'), max_digits=9, decimal_places=2)
    tax = models.DecimalField(_('tax'), max_digits=9, decimal_places=2, blank=True)
    shipping = models.DecimalField(_('shipping'), max_digits=9, decimal_places=2, blank=True)
    handling_fee = models.DecimalField(_('handling fee'), max_digits=9, decimal_places=2, blank=True)
    shipping_discount = models.DecimalField(_('shipping discount'), max_digits=9, decimal_places=2, blank=True)
    insurance = models.DecimalField(_('insurance fee'), max_digits=9, decimal_places=2, blank=True)
    gift_wrap = models.DecimalField(_('gift wrap fee'), max_digits=9, decimal_places=2, blank=True)

    reference_id = models.CharField(_('reference id'), max_length=255, blank=True)
    settlement_destination = models.CharField(_('settlement destination'), max_length=255, default='PARTNER_BALANCE')
    allowed_payment_method = models.CharField(
        _('allowed payment method'), max_length=255, default='INSTANT_FUNDING_SOURCE'
    )  # UNRESTRICTED or INSTANT_FUNDING_SOURCE or IMMEDIATE_PAY
    description = models.CharField(_('description'), max_length=255, blank=True)
    note_to_payee = models.CharField(_('note to payee'), max_length=255, blank=True)
    custom = models.CharField(_('custom'), max_length=127, blank=True)
    invoice_number = models.CharField(_('invoice number'), max_length=127)
    purchase_order = models.CharField(_('purchase order'), max_length=127)
    soft_descriptor = models.CharField(_('soft descriptor'), max_length=22)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    last_modified = models.DateTimeField(_('last modified'), auto_now=True)

    shipping_method = models.CharField(_('shipping method'), max_length=255, blank=True)
    shipping_phone_number = models.CharField(_('shipping phone number'), max_length=255, blank=True)

    shipping_address_line_1 = models.CharField(_('shipping address line 1'), max_length=100)  # number, street, etc.
    shipping_address_line_2 = models.CharField(_('shipping address line 2'), max_length=100, blank=True)  # apt number, etc.
    shipping_address_city = models.CharField(_('shipping address city'), max_length=50)
    shipping_address_country = models.CharField(_('shipping address country'), max_length=2)
    shipping_address_postal_code = models.CharField(
        _('shipping address postal code'), max_length=20, blank=True
    )  # required in certain countries
    shipping_address_state = models.CharField(_('shipping address state'), max_length=100, blank=True)
    shipping_address_phone = models.CharField(_('shipping address phone'), max_length=50)
    shipping_address_normalization_status = models.CharField(
        _('shipping address normalization status'), max_length=50, default='UNKNOWN'
    )  # UNKNOWN or UNNORMALIZED_USER_PREFERRED or NORMALIZED or UNNORMALIZED
    shipping_address_type = models.CharField(
        _('shipping address type'), max_length=50, default='HOME_OR_WORK'
    )  # HOME_OR_WORK or GIFT or other
    shipping_address_recipient_name = models.CharField(_('shipping address recipient name'), max_length=127)

    objects = models.Manager()

    def __str__(self):
        return '{} - {} {}'.format(self.reference_id, self.total_amount, self.currency)

    class Meta:
        verbose_name = _('Legacy Paypal Transaction (payments v1 API)')
        verbose_name_plural = _('Legacy Paypal Transactions (payments v1 API)')


class LegacyPaypalItem(models.Model):
    transaction = models.ForeignKey(LegacyPaypalTransaction, verbose_name=_('transaction'), related_name='items', on_delete=models.PROTECT)

    sku = models.CharField(_('stock keeping unit'), max_length=127)
    name = models.CharField(_('name'), max_length=127)
    description = models.CharField(_('description'), max_length=127, blank=True)
    quantity = models.CharField(_('quantity'), max_length=10)
    price = models.CharField(_('price'), max_length=10)
    currency = models.CharField(_('currency'), max_length=3)
    tax = models.CharField(_('currency'), max_length=10, blank=True)
    url = models.URLField(_('url'), blank=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    last_modified = models.DateTimeField(_('last modified'), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Legacy Paypal Item (payments v1 API)')
        verbose_name_plural = _('Legacy Paypal Item (payments v1 API)')
