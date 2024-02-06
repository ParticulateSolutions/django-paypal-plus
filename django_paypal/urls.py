from django.urls import re_path

from .webhooks import PaypalWebhookView

urlpatterns = [
    re_path(r'^webhooks/$', PaypalWebhookView.as_view(), name='paypal-webhooks'),
]
