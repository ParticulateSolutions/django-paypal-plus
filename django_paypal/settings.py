from django.conf import settings

from django_paypal.__init__ import __version__

DJANGO_PAYPAL_VERSION = __version__

PAYPAL_API_CLIENT_ID = getattr(settings, 'PAYPAL_API_CLIENT_ID', False)
PAYPAL_API_SECRET = getattr(settings, 'PAYPAL_API_SECRET', False)

PAYPAL_API_URL = getattr(settings, 'PAYPAL_API_URL', 'https://api.paypal.com')
PAYPAL_SANDBOX_API_URL = getattr(settings, 'PAYPAL_SANDBOX_API_URL', 'https://api.sandbox.paypal.com')
PAYPAL_SANDBOX = getattr(settings, 'PAYPAL_SANDBOX', True)

PAYPAL_AUTH_URL = getattr(settings, 'PAYPAL_AUTH_URL', '/v1/oauth2/token')
PAYPAL_PAYMENT_URL = getattr(settings, 'PAYPAL_PAYMENT_URL', '/v1/payments/payment')

# checkout urls
PAYPAL_SUCCESS_URL = getattr(settings, 'PAYPAL_SUCCESS_URL', '/')
PAYPAL_CANCELLATION_URL = getattr(settings, 'PAYDIREKT_CANCELLATION_URL', '/')
PAYPAL_NOTIFICATION_URL = getattr(settings, 'PAYDIREKT_NOTIFICATION_URL', '/paypal/notify/')

if getattr(settings, 'PAYPAL', False):
    PAYPAL_ROOT_URL = settings.PAYPAL_ROOT_URL
