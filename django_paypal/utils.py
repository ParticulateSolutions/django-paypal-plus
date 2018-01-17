from django_paypal import settings as django_paypal_settings


def build_paypal_full_uri(url):
    if url.startswith('/'):
        url = '{0}{1}'.format(django_paypal_settings.PAYPAL_ROOT_URL, url)
    return url
