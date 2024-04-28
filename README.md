[//]: # (# django-paypal-plus [![Build Status]&#40;https://travis-ci.org/ParticulateSolutions/django-paypal-plus.svg?branch=master&#41;]&#40;https://travis-ci.org/ParticulateSolutions/django-paypal-plus&#41;)
[![Stable Version](https://img.shields.io/pypi/v/django-paypal-plus?color=blue)](https://pypi.org/project/django-paypal-plus/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

`django-paypal-plus` is a Django plugin that provides integration with PayPal's Orders API and Webhooks API. The package allows for the creation, management, and updating of orders through PayPal's Orders API. It also includes support for creating and listening to webhooks, enabling real-time communication between your application and PayPal's servers for capturing order events.

## Installation

The installation process for django-paypal-plus is straightforward and consists of two main steps:

1. Install the package in your virtual environment using pip:

	```bash
	pip install django-paypal-plus
	```

2. Configure your Django project by adding the following lines to your settings file:

	```python
	# django-paypal-plus
	INSTALLED_APPS += ('django_paypal', )
	
	PAYPAL = True
	
	# Replace the following dummy values with your own PayPal API credentials. These are used in our default webhook view.
	PAYPAL_API_CLIENT_ID = "Your-PayPal-Client-ID"
	PAYPAL_API_SECRET = "Your-PayPal-Secret"
	
	# Optional settings
	PAYPAL_AUTH_CACHE_KEY = "paypal_auth_cache_key" # Default is "django-paypal-auth"
	PAYPAL_AUTH_CACHE_TIMEOUT = 3600 # Default is 600 seconds
	PAYPAL_WEBHOOK_ID = "Your-PayPal-Webhook-ID" # Default is None
	```


## Requirements

```
1. Django >= 2.2
2. Python >= 3.8
```

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
