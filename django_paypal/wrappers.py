from __future__ import unicode_literals

import base64
import json
import logging
import os
import sys
from decimal import Decimal

import certifi
from django.conf import settings

from django_paypal import settings as django_paypal_settings
from django_paypal.models import PaypalTransaction, PaypalPayment, PaypalItem
from django_paypal.utils import build_paypal_full_uri

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import HTTPError, Request, urlopen


class PaypalWrapper(object):
    interface_version = 'django_paypal_v{}'.format(django_paypal_settings.DJANGO_PAYPAL_VERSION)

    api_url = django_paypal_settings.PAYPAL_API_URL
    sandbox_url = django_paypal_settings.PAYPAL_SANDBOX_API_URL
    payment_url = django_paypal_settings.PAYPAL_PAYMENT_URL
    auth_url = django_paypal_settings.PAYPAL_AUTH_URL

    auth = None

    def __init__(self, auth=None, sandbox=None):
        super(PaypalWrapper, self).__init__()
        if getattr(settings, 'PAYPAL', False):
            self.auth = auth
            if sandbox is not None:
                if sandbox:
                    self.api_url = self.sandbox_url
            else:
                if django_paypal_settings.PAYPAL_SANDBOX:
                    self.api_url = self.sandbox_url

    def init(self, intent, payer, transactions, note_to_payer=None, experience_profile_id=None,
             success_url=django_paypal_settings.PAYPAL_SUCCESS_URL,
             cancellation_url=django_paypal_settings.PAYPAL_CANCELLATION_URL,
             notification_url=django_paypal_settings.PAYPAL_NOTIFICATION_URL):

        if not self.auth:
            return False

        # for transaction in transactions:
        #     transaction['notify_url'] = build_paypal_full_uri(notification_url)
        payment_data = {
            'intent': intent,
            'payer': payer,
            'transactions': transactions
        }
        if experience_profile_id:
            payment_data.update({'experience_profile_id': experience_profile_id})
        if note_to_payer:
            payment_data.update({'note_to_payer': note_to_payer})
        if note_to_payer:
            payment_data.update(
                {'redirect_urls':
                    {'return_url': build_paypal_full_uri(success_url),
                     'cancel_url': build_paypal_full_uri(cancellation_url)}
                 })

        payment_response = self.call_api(url=self.payment_url, data=payment_data)

        if payment_response and 'state' in payment_response and payment_response['state'] == 'created':

            transaction_array = []
            items_dict = {}
            try:
                paypal_payment = PaypalPayment(
                    state=payment_response['state'],
                    payment_id=payment_response['id'],
                    intent=payment_response['intent'],
                    experience_profile_id=payment_response.get('experience_profile_id', ''),
                    note_to_payer=payment_response.get('note_to_payer', ''),
                    payment_method=payment_response['payer'].get('payment_method', ''),
                    custom=payment_response.get('custom', ''),
                    initial_response_object=json.dumps(payment_response),
                )
                if 'links' in payment_response:
                    for link in payment_response['links']:
                        if 'rel' in link:
                            if link['rel'] == "self":
                                paypal_payment.link = link['href']
                            elif link['rel'] == "approval_url":
                                paypal_payment.approve_link = link['href']
                            elif link['rel'] == "execute":
                                paypal_payment.execute_link = link['href']

                for transaction in payment_response['transactions']:
                    transaction_array.append(PaypalTransaction(
                        reference_id=transaction['reference_id'],
                        total_amount=Decimal(transaction['amount']['total']),
                        currency=transaction['amount']['currency'],
                        subtotal=Decimal(transaction['amount']['details'].get('subtotal', 0)),
                        tax=Decimal(transaction['amount']['details'].get('tax', 0)),
                        shipping=Decimal(transaction['amount']['details'].get('shipping', 0)),
                        handling_fee=Decimal(transaction['amount']['details'].get('handling_fee', 0)),
                        shipping_discount=Decimal(transaction['amount']['details'].get('shipping_discount', 0)),
                        insurance=Decimal(transaction['amount']['details'].get('insurance', 0)),
                        gift_wrap=Decimal(transaction['amount']['details'].get('gift_wrap', 0)),
                        settlement_destination=transaction.get('settlement_destination', ''),
                        allowed_payment_method=transaction['payment_options'].get('allowed_payment_method', ''),
                        description=transaction.get('description', ''),
                        note_to_payee=transaction.get('note_to_payee', ''),
                        custom=transaction.get('custom', ''),
                        invoice_number=transaction.get('invoice_number', ''),
                        purchase_order=transaction.get('purchase_order', ''),
                        soft_descriptor=transaction.get('soft_descriptor', ''),
                        shipping_method=transaction['item_list'].get('shipping_method', ''),
                        shipping_phone_number=transaction['item_list'].get('shipping_phone_number', ''),
                        shipping_address_line_1=transaction['item_list']['shipping_address'].get('line_1', ''),
                        shipping_address_line_2=transaction['item_list']['shipping_address'].get('line_2', ''),
                        shipping_address_city=transaction['item_list']['shipping_address'].get('city', ''),
                        shipping_address_country=transaction['item_list']['shipping_address'].get('country', ''),
                        shipping_address_postal_code=transaction['item_list']['shipping_address'].get('postal_code', ''),
                        shipping_address_state=transaction['item_list']['shipping_address'].get('state', ''),
                        shipping_address_phone=transaction['item_list']['shipping_address'].get('phone', ''),
                        shipping_address_normalization_status=transaction['item_list']['shipping_address'].get('normalization_status', ''),
                        shipping_address_type=transaction['item_list']['shipping_address'].get('type', ''),
                        shipping_address_recipient_name=transaction['item_list']['shipping_address'].get('recipient_name', ''),
                    ))
                    for item in transaction['item_list']['items']:
                        if transaction['reference_id'] not in items_dict:
                            items_dict[transaction['reference_id']] = []
                        items_dict[transaction['reference_id']].append(PaypalItem(
                            sku=item.get('sku', ''),
                            name=item.get('name', ''),
                            description=item['description'],
                            quantity=item['quantity'],
                            price=item['price'],
                            currency=item['currency'],
                            tax=item.get('tax', ''),
                            url=item.get('url', '')
                        ))
            except KeyError as e:
                return False
            paypal_payment.save()
            for transaction in transaction_array:
                transaction.payment = paypal_payment
                transaction.save()
                if transaction.reference_id in items_dict:
                    for item in items_dict[transaction.reference_id]:
                        item.transaction = transaction
                        item.save()
            return paypal_payment
        else:
            return False

    def call_api(self, url=None, access_token=None, data=None):
        if not self.auth:
            return False
        if not url.lower().startswith('http'):
            url = '{0}{1}'.format(self.api_url, url)
        request = Request(url)

        if access_token is None:
            access_token = self._get_access_token()
        request.add_header('Authorization', 'Bearer {0}'.format(access_token))
        if data:
            data = json.dumps(data)
            data_len = len(data)
            request.add_header('Content-Length', data_len)
            request.data = data.encode(encoding='utf-8')
        elif data == '':
            request.method = 'POST'
            request.data = ''.encode(encoding='utf-8')
        request.add_header('Content-Type', 'application/json')
        try:
            if sys.version_info.major > 2 or (sys.version_info.major == 2 and sys.version_info.major > 7 or (sys.version_info.major == 7 and sys.version_info.major >= 9)):
                response = urlopen(request, cafile=certifi.where())
            else:
                response = urlopen(request)
        except HTTPError as e:
            logger = logging.getLogger(__name__)
            fp = e.fp
            body = fp.read()
            fp.close()
            if hasattr(e, 'code'):
                logger.error("Paypal Error {0}({1}): {2}".format(e.code, e.msg, body))
            else:
                logger.error("Paypal Error({0}): {1}".format(e.msg, body))
        else:
            return json.loads(response.read().decode('utf-8'))
        return False

    def _get_access_token(self):
        url = '{0}{1}'.format(self.api_url, self.auth_url)
        request = Request(url=url)
        # preparing request
        base64string = base64.encodestring(('%s:%s' % (self.auth['API_CLIENT_ID'], self.auth['API_SECRET'])).encode()).decode().replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        data = "grant_type=client_credentials"
        data_len = len(data)
        request.add_header('Accept', 'application/json')
        request.add_header('Content-Length', data_len)
        request.data = data.encode(encoding='utf-8')

        try:
            if sys.version_info.major > 2 or (sys.version_info.major == 2 and sys.version_info.major > 7 or (sys.version_info.major == 7 and sys.version_info.major >= 9)):
                response = urlopen(request, cafile=certifi.where())
            else:
                response = urlopen(request)
        except HTTPError as e:
            logger = logging.getLogger(__name__)
            fp = e.fp
            body = fp.read()
            fp.close()
            if hasattr(e, 'code'):
                logger.error("Paypal Error {0}({1}): {2}".format(e.code, e.msg, body))
            else:
                logger.error("Paypal Error({0}): {1}".format(e.msg, body))
        else:
            return json.loads(response.read().decode('utf-8'))['access_token']
