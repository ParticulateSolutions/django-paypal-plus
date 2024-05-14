import json
from typing import Any, Dict

from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .api_types import APIAuthCredentials
from .models import PaypalWebhook, PaypalWebhookEvent, PaypalOrder
from .signals import order_approved, order_completed
from .wrappers import PaypalWrapper
from django_paypal import settings as django_paypal_settings


class WebhookEvents:
    ORDERS = ['CHECKOUT.ORDER.COMPLETED', 'CHECKOUT.ORDER.APPROVED', 'CHECKOUT.PAYMENT-APPROVAL.REVERSED']


def verify_and_save_webhook_event(request: HttpRequest, paypal_wrapper: PaypalWrapper, payload: Dict[str, Any]):
    if not settings.DEBUG:
        paypal_webhook = PaypalWebhook.objects.get(url=request.build_absolute_uri(), auth_hash=paypal_wrapper.api_auth_hash)
        paypal_wrapper.verify_webhook_event(request, paypal_webhook.webhook_id)
        try:
            paypal_order = PaypalOrder.objects.get(order_id=payload['resource']['id'])
        except (KeyError, TypeError):  # if the payload does not contain the order id
            paypal_order = None
        event_data = {'payload': payload, 'webhook': paypal_webhook, 'order': paypal_order}
        PaypalWebhookEvent.objects.create(**event_data)


@method_decorator(csrf_exempt, name='dispatch')
class PaypalWebhookView(View):
    def post(self, request, *args, **kwargs):
        post_dict = json.loads(request.body.decode('utf-8'))
        event_type = post_dict.get('event_type')
        if event_type not in WebhookEvents.ORDERS:
            return HttpResponse(status=400)

        paypal_wrapper = PaypalWrapper(
            auth=APIAuthCredentials(
                client_id=django_paypal_settings.PAYPAL_API_CLIENT_ID, client_secret=django_paypal_settings.PAYPAL_API_SECRET
            )
        )

        verify_and_save_webhook_event(request, paypal_wrapper, payload=post_dict)

        if event_type == 'CHECKOUT.ORDER.APPROVED':
            order_approved.send(sender=self.__class__, resource=post_dict.get('resource'))
            paypal_wrapper.capture_order(post_dict.get('resource').get('id'))
        if event_type == 'CHECKOUT.ORDER.COMPLETED':
            order_completed.send(sender=self.__class__, resource=post_dict.get('resource'))

        return HttpResponse(status=200)
