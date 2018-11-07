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
    PAYPAL_ROOT_URL = 'https://example.com"

	```


## What do you need for django-paypal-plus?

1. Django >= 1.8

## Usage

```python
paypal_wrapper = PaypalWrapper(auth={
    'API_CLIENT_ID': settings.PAYPAL_API_CLIENT_ID,
    'API_SECRET': settings.PAYPAL_API_SECRET
})
amount = 10
transactions = [{
    "reference_id": 1234,
    "amount": {
        "total": amount,
        "currency": "EUR",
        "details": {
            "subtotal": amount,
        }
    },
    "payment_options": {
        "allowed_payment_method": "INSTANT_FUNDING_SOURCE"
    },
    "item_list": {
        "items": [{
            "name": "Donation",
            "description": "My donation",
            "quantity": "1",
            "price": amount,
            "currency": "EUR"
        }],
        "shipping_address": {
            "recipient_name": "Particulate Solutions GmbH",
            "line1": "Universitaetsstrasse 3",
            "city": "Koblenz",
            "country_code": "DE",
            "postal_code": "56070"
        }
    }
}]

paypal_payment = paypal_wrapper.init(
    intent='sale',
    payer={'payment_method': 'paypal'},
    note_to_payer="My donation",
    cancellation_url=cancelled_url,
    transactions=transactions,
    success_url=request.build_absolute_uri(reverse('paypal_donation_success', kwargs={'reference_number': 1234})),
)
```

Here is an example to check if a payment was approved:
```python
is_updated = paypal_payment.refresh_from_paypal(paypal_wrapper=paypal_wrapper)
if is_updated and paypal_payment.state == 'approved':
    # open the PayPal window using NotifyPaypalView
```

## Copyright and license

Copyright 2017-2018 Jonas Braun for Particulate Solutions GmbH, under [MIT license](https://github.com/minddust/bootstrap-progressbar/blob/master/LICENSE).
