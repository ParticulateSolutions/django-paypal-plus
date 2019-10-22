import json

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .wrappers import PaypalWrapper
from .models import PaypalPayment
from django_paypal import settings as django_paypal_settings


class NotifyPaypalView(View):
    paypal_wrapper = PaypalWrapper(auth={
        'API_CLIENT_ID': django_paypal_settings.PAYPAL_API_CLIENT_ID,
        'API_SECRET': django_paypal_settings.PAYPAL_API_SECRET,
    })

    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body.decode('utf-8'))

        # return HttpResponse(status=200)
        # general attributes
        if 'resource' not in request_data:
            return HttpResponse(status=400)
        payment_id = None
        for key in ['parent_payment', 'id']:
            if key in request_data['resource']:
                payment_id = request_data['resource'][key]
                break
        if payment_id is None:
            return HttpResponse(status=400)

        try:
            paypal_payment = PaypalPayment.objects.get(payment_id=payment_id)
        except PaypalPayment.DoesNotExist:
            return HttpResponse(status=400)
        return self.handle_updated_payment(paypal_payment=paypal_payment, expected_status='approved')

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(NotifyPaypalView, self).dispatch(request, *args, **kwargs)

    def handle_updated_payment(self, paypal_payment, expected_status=None):
        """
            Override to use the paypal_payment in the way you want.
        """
        updated_payment = paypal_payment
        if updated_payment.refresh_from_paypal(self.paypal_wrapper, expected_status=expected_status):
            if updated_payment.status == 'approved':
                import logging
                logger = logging.getLogger(__name__)
                logger.error(_('Paypal: Status of checkout {} is now {}').format(updated_payment.payment_id, updated_payment.status))
                return HttpResponse(status=400)
            return HttpResponse(status=200)
        return HttpResponse(status=400)
