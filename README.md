# django-paypal-plus [![Build Status](https://travis-ci.org/ParticulateSolutions/django-paypal-plus.svg?branch=master)](https://travis-ci.org/ParticulateSolutions/django-paypal-plus)

`django-paypal` is a lightweight [django](http://djangoproject.com) plugin which provides the integration of the payment provider [PayPal](https://paypal.com).

## How to install django-paypal-plus?

There are just two steps needed to install django-paypal-plus:

1. Install django-paypal-plus to your virtual env:

	```bash
	pip install django-paypal-plus
	```

2. Configure your django installation with the following lines:

	```python
    # django-paypal-plus
    INSTALLED_APPS += ('django_paypal', )

    PAYPAL = True

    # Those are dummy test data - change to your data
    PAYPAL_API_CLIENT_ID = "Your-PayPal-Client-ID"
    PAYPAL_API_SECRET = "Your-PayPal-Secret"
 	PAYPAL_AUTH_CACHE_KEY = "paypal_auth_cache_key" (optional, default is "django-paypal-auth")
 	PAYPAL_AUTH_CACHE_TIMEOUT = 3600 (optional, default is 600 seconds)
 	PAYPAL_WEBHOOK_ID = "Your-PayPal-Webhook-ID" (optional, default is None)

	```


## What do you need for django-paypal-plus?

1. Django >= 2.2
2. Python >= 3.8

## Usage


### Create a new order
```python
paypal_wrapper = PaypalWrapper(
	auth=APIAuthCredentials(
		client_id=django_paypal_settings.PAYPAL_API_CLIENT_ID, client_secret=django_paypal_settings.PAYPAL_API_SECRET
	)
)


paypal_order = paypal_wrapper.create_order(
	intent='sale',
	intent='CAPTURE',
	payer={'payment_method': 'paypal'},
	purchase_units=<purchase_units>,
	note_to_payer="Thank you for your purchase!",
	payment_source=paypal_api.PaymentSource(paypal=paypal_api.PayPal()),
	cancellation_url=<cancelled_url>,
	transactions=<transactions>,
	success_url=<my success url>
)
```

### Capture an order
```python
paypal_wrapper.capture_order(resource_id)
```

### Listening to webhooks

By default, django-paypal-plus has a ``PaypalWebhookView`` listening to Order events. If you haven't already set up webhooks on PayPal,
``paypal_wrapper.setup_webhooks(<webhook_url>)`` will do that for you.

## Copyright and license

Copyright 2024 - Tim Burg for Particulate Solutions GmbH, under [MIT license](https://github.com/minddust/bootstrap-progressbar/blob/master/LICENSE).
