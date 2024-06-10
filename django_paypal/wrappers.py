from __future__ import unicode_literals

import hashlib
import json
import warnings
from typing import Literal, List, Any, Dict

from django.core.cache import cache
import requests
from django.http import HttpRequest
from requests.auth import HTTPBasicAuth

from django_paypal import settings as django_paypal_settings
from django_paypal.exceptions import PaypalAuthFailure, PaypalAPIError, PaypalWebhookVerificationError, PaypalOrderAlreadyCapturedError
from django_paypal.models import (
    PaypalOrder,
    PaypalAPIPostData,
    PaypalAPIResponse,
    PaypalWebhook,
)
from django_paypal.api_types import (
    OAuthResponse,
    PaymentSource,
    ApplicationContext,
    ExperienceContext,
    PurchaseUnit,
    APIAuthCredentials,
    OrderCreatedAPIResponse,
    OrderCaptureAPIResponse,
    OrderDetailAPIResponse,
)
from django_paypal.utils import build_paypal_full_uri
from django_paypal.signals import order_captured, order_created


class PaypalWrapper(object):
    interface_version = 'django_paypal_v{}'.format(django_paypal_settings.DJANGO_PAYPAL_VERSION)

    api_url = django_paypal_settings.PAYPAL_API_URL
    sandbox_url = django_paypal_settings.PAYPAL_SANDBOX_API_URL
    orders_api_endpoint = django_paypal_settings.PAYPAL_ORDERS_API_ENDPOINT
    auth_url = django_paypal_settings.PAYPAL_AUTH_URL
    auth_cache_timeout = django_paypal_settings.PAYPAL_AUTH_CACHE_TIMEOUT
    auth_cache_key = django_paypal_settings.PAYPAL_AUTH_CACHE_KEY

    auth: APIAuthCredentials = None

    def __init__(self, auth: APIAuthCredentials, sandbox=None):
        super(PaypalWrapper, self).__init__()
        self.auth = auth
        if sandbox or django_paypal_settings.PAYPAL_SANDBOX:
            self.api_url = self.sandbox_url

    def create_order(
        self,
        intent: Literal['CAPTURE', 'AUTHORIZE'],
        purchase_units: List[PurchaseUnit],
        payment_source: PaymentSource,
        application_context: ApplicationContext = None,
        success_url=django_paypal_settings.PAYPAL_SUCCESS_URL,
        cancellation_url=django_paypal_settings.PAYPAL_CANCELLATION_URL,
    ) -> OrderCreatedAPIResponse:
        if payment_source.paypal and (success_url or cancellation_url):
            if not payment_source.paypal.experience_context:
                payment_source.paypal.experience_context = ExperienceContext(
                    return_url=build_paypal_full_uri(success_url),
                    cancel_url=build_paypal_full_uri(cancellation_url),
                )
            else:
                if not payment_source.paypal.experience_context.return_url:
                    payment_source.paypal.experience_context.return_url = build_paypal_full_uri(success_url)
                if not payment_source.paypal.experience_context.cancel_url:
                    payment_source.paypal.experience_context.cancel_url = build_paypal_full_uri(cancellation_url)

        order_data = {'intent': intent, 'purchase_units': [purchase_unit.to_dict() for purchase_unit in purchase_units]}
        if payment_source:
            order_data.update({'payment_source': payment_source.to_dict()})
        if application_context:
            order_data.update({'application_context': application_context.to_dict()})

        url = '{0}{1}'.format(self.api_url, self.orders_api_endpoint)
        order_response_dict = self.call_api(url=url, data=order_data, method='POST')
        order_response = OrderCreatedAPIResponse.from_dict(order_response_dict)
        new_order = PaypalOrder.objects.create(order_id=order_response.id, status=order_response.status)
        post_obj = PaypalAPIPostData.objects.create(order=new_order, url=url, post_data=order_data)
        PaypalAPIResponse.objects.create(order=new_order, url=url, response_data=order_response_dict, post=post_obj)
        order_created.send(sender=self.__class__, order=new_order, response=order_response_dict)
        return order_response

    def capture_order(self, order_id: str) -> OrderCaptureAPIResponse:
        order = PaypalOrder.objects.get(order_id=order_id)
        url = f'{self.api_url}{self.orders_api_endpoint}/{order.order_id}/capture'

        try:
            order_capture_response = self.call_api(url=url, method='POST')
        except PaypalAPIError as e:
            if e.response.status_code == 422:
                order_capture_response = e.response.json()
                if order_capture_response.get('name') == 'UNPROCESSABLE_ENTITY':
                    if order_capture_response['details'][0]['issue'] == 'ORDER_ALREADY_CAPTURED':
                        raise PaypalOrderAlreadyCapturedError(str(e), response=e.response)

        order_capture = OrderCaptureAPIResponse.from_dict(order_capture_response)
        order.status = order_capture.status
        order.save(update_fields=['status'])
        post_obj = PaypalAPIPostData.objects.create(order=order, url=url, post_data={})
        PaypalAPIResponse.objects.create(order=order, url=url, response_data=order_capture_response, post=post_obj)
        order_captured.send(sender=self.__class__, order=order, response=order_capture_response)
        return order_capture

    def get_order_details(self, order_id: str) -> OrderDetailAPIResponse:
        order = PaypalOrder.objects.get(order_id=order_id)
        url = f'{self.api_url}{self.orders_api_endpoint}/{order.order_id}'
        order_details_response = self.call_api(url=url, method='GET')
        return OrderDetailAPIResponse.from_dict(order_details_response)

    def call_api(self, url: str, method: Literal['GET', 'POST', 'PATCH', 'DELETE'], data=None) -> Dict[str, Any]:
        headers = {'Authorization': f'Bearer {self._get_access_token()}', 'Content-Type': 'application/json'}

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
                response.raise_for_status()
                return {'deleted': True}
            else:
                raise ValueError('Invalid method')
            response.raise_for_status()
            response_json = response.json()
            return response_json
        except requests.HTTPError as e:
            raise PaypalAPIError(str(e), response=e.response)

    def setup_webhooks(self, webhook_listener: str) -> PaypalWebhook:
        if PaypalWebhook.objects.filter(url=webhook_listener, auth_hash=self.api_auth_hash).exists():
            raise ValueError(f'Webhook listener ({webhook_listener}) already exists')
        from django_paypal.webhooks import WebhookEvents

        data = {'url': webhook_listener, 'event_types': [{'name': event} for event in WebhookEvents.ORDERS]}
        webhook_api = '{0}{1}'.format(self.api_url, '/v1/notifications/webhooks')
        try:
            response_dict = self.call_api(url=webhook_api, method='POST', data=data)
            return PaypalWebhook.objects.create(
                webhook_id=response_dict['id'],
                auth_hash=self.api_auth_hash,
                url=response_dict['url'],
                event_types=response_dict['event_types'],
            )
        except PaypalAPIError as e:
            response_json = e.response.json()
            if response_json.get('name') == 'WEBHOOK_URL_ALREADY_EXISTS':
                webhook_list = self.call_api(url=webhook_api, method='GET')
                for webhook in webhook_list.get('webhooks', []):
                    if webhook['url'] == webhook_listener:
                        return PaypalWebhook.objects.create(
                            webhook_id=webhook['id'], url=webhook['url'], event_types=webhook['event_types'], auth_hash=self.api_auth_hash
                        )
            raise e

    def patch_webhook(self, webhook_id: str, patch_data: List[Dict]) -> PaypalWebhook:
        try:
            paypal_webhook = PaypalWebhook.objects.get(webhook_id=webhook_id)
        except PaypalWebhook.DoesNotExist as e:
            warnings.warn(f'Webhook with id {webhook_id} does not exist in the database. Set up webhooks by calling "setup_webhooks"')
            raise e
        url = '{0}{1}'.format(self.api_url, f'/v1/notifications/webhooks/{paypal_webhook.webhook_id}')
        webhook_response_dict = self.call_api(url=url, method='PATCH', data=patch_data)
        paypal_webhook.url = webhook_response_dict['url']
        paypal_webhook.event_types = webhook_response_dict['event_types']
        paypal_webhook.save()
        return paypal_webhook

    def delete_webhook(self, webhook_listener: str) -> bool:
        try:
            paypal_webhook = PaypalWebhook.objects.get(url=webhook_listener, auth_hash=self.api_auth_hash)
        except PaypalWebhook.DoesNotExist as e:
            raise e
        url = '{0}{1}'.format(self.api_url, f'/v1/notifications/webhooks/{paypal_webhook.webhook_id}')
        self.call_api(url=url, method='DELETE')
        paypal_webhook.delete()
        return True

    def verify_webhook_event(self, request: HttpRequest, webhook_id: str) -> bool:
        headers = request.headers
        auth_algo = headers.get('Paypal-Auth-Algo')
        cert_url = headers.get('Paypal-Cert-Url')
        transmission_id = headers.get('Paypal-Transmission-Id')
        transmission_time = headers.get('Paypal-Transmission-Time')
        transmission_sig = headers.get('Paypal-Transmission-Sig')
        request_data = json.loads(request.body.decode('utf-8'))
        verification_payload = {
            'auth_algo': auth_algo,
            'cert_url': cert_url,
            'transmission_id': transmission_id,
            'transmission_time': transmission_time,
            'transmission_sig': transmission_sig,
            'webhook_id': webhook_id,
            'webhook_event': request_data,
        }
        url = f'{self.api_url}/v1/notifications/verify-webhook-signature'
        res = self.call_api(url=url, method='POST', data=verification_payload)
        if res.get('verification_status') == 'SUCCESS':
            return True
        raise PaypalWebhookVerificationError('Webhook verification failed', res)

    def verify_api_keys(self) -> bool:
        self._get_access_token()
        return True

    def _get_access_token(self) -> str:
        if not self.auth_cache_timeout:
            auth_response = self._authorize_client()
            return auth_response.access_token
        else:
            cache_key = self.auth_cache_key.format(auth_hash=self.api_auth_hash)
            access_token = cache.get(cache_key)
            if not access_token:
                auth_response = self._authorize_client()
                access_token = auth_response.access_token
                cache.set(cache_key, access_token, self.auth_cache_timeout)
            return access_token

    def _authorize_client(self) -> OAuthResponse:
        # preparing request
        url = f'{self.api_url}{self.auth_url}'

        api_auth = HTTPBasicAuth(self.auth.client_id, self.auth.client_secret)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'client_credentials'}

        try:
            response = requests.post(url, headers=headers, data=data, auth=api_auth)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_json = response.json()
            return OAuthResponse(**response_json)
        except requests.HTTPError as e:
            raise PaypalAuthFailure(str(e), response=e.response)

    @property
    def api_auth_hash(self) -> str:
        return hashlib.md5(f'{self.auth.client_id}{self.auth.client_secret}'.encode()).hexdigest()
