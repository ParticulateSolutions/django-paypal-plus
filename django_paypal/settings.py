from django.conf import settings

from django_paypal.__init__ import __version__

DJANGO_PAYPAL_VERSION = __version__

PAYPAL_API_CLIENT_ID = getattr(settings, 'PAYPAL_API_CLIENT_ID', False)
PAYPAL_API_SECRET = getattr(settings, 'PAYPAL_API_SECRET', False)

PAYPAL_API_URL = getattr(settings, 'PAYPAL_API_URL', 'https://api-m.paypal.com')
PAYPAL_SANDBOX_API_URL = getattr(settings, 'PAYPAL_SANDBOX_API_URL', 'https://api-m.sandbox.paypal.com')
PAYPAL_SANDBOX = getattr(settings, 'PAYPAL_SANDBOX', True)

PAYPAL_AUTH_URL = getattr(settings, 'PAYPAL_AUTH_URL', '/v1/oauth2/token')
PAYPAL_AUTH_CACHE_TIMEOUT = getattr(settings, 'PAYPAL_AUTH_CACHE_TIMEOUT', 600)  # 10 minutes
PAYPAL_AUTH_CACHE_KEY = getattr(settings, 'PAYPAL_AUTH_CACHE_KEY', 'django-paypal-auth-{auth_hash}')
PAYPAL_ORDERS_API_ENDPOINT = getattr(settings, 'PAYPAL_ORDERS_API_ENDPOINT', '/v2/checkout/orders')
PAYPAL_WEBHOOK_LISTENER = getattr(settings, 'PAYPAL_WEBHOOK_LISTENER', None)

# checkout urls
PAYPAL_SUCCESS_URL = getattr(settings, 'PAYPAL_SUCCESS_URL', '/')
PAYPAL_CANCELLATION_URL = getattr(settings, 'PAYDIREKT_CANCELLATION_URL', '/')
PAYPAL_NOTIFICATION_URL = getattr(settings, 'PAYDIREKT_NOTIFICATION_URL', '/paypal/notify/')

if getattr(settings, 'PAYPAL', False):
    PAYPAL_ROOT_URL = settings.PAYPAL_ROOT_URL
