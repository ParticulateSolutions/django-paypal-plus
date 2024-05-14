# Changelog

## v1.1.1
### Bugfixes
* Fixed bug in retrieving correct webhook when multiple webhooks are set up for the same endpoint

---

## v1.1.0
### Features
* Added support for multiple API keys using the same webhook endpoint
* `PaypalWebhook` model has been extended by new field `auth_hash`. This allows to have multiple webhooks for the same endpoint
  but with different API keys and clearly mapping webhook objects to your `PaypalWrapper` instance.
* Added `api_auth_hash` property to `PaypalWrapper` to get a hash of API key + secret. This is used to create and find unique webhooks.
* Added `delete_webhook` method to `PaypalWrapper` to delete webhooks (both in PayPal and in the database)
* Added `verify_api_keys` method to `PaypalWrapper` to verify that the API keys are valid
### Breaking Changes
* `setup_webhooks` now uses a hash created from the API key + secret to create unique webhooks. This means that if you call
the existing `setup_webhooks` method, it will create new webhooks for the same API key as the check is now on both key and url.
Since we don't save API keys anywhere in this library, you will need to update existing webhooks yourself. This should be relatively easy
since, as before this version, each endpoint is clearly mapped to only one `PaypalWebhook` object. Iterate through your API keys, create a new `PaypalWrapper`
instance, get its corresponding webhook, and update it by setting `webhook.auth_hash = paypal_wrapper.api_auth_hash` and calling `webhook.save()`.


---


### v1.0.1
* Fixed bug in webhook verficiation on production

---

# v1.0.0

### Breaking Changes

* Renamed PaypalPayment to LegacyPaypalPayment (Deprecation of PaypalPayment)
* Renamed PaypalTransaction to LegacyPaypalTransaction (Deprecation of PaypalTransaction)
* Rewrote PaypalWrapper. Check class as pretty much everything changed
* Using Paypal Order v2 API instead of Paypal Payment v1 API

### Features

* Added new models to track Orders and API calls/responses
* Rewrote PaypalWrapper and added new methods to handle Orders and API calls/responses
* Added Dataclasses for PaypalWrapper and API calls/responses
* Added Webhook support for Orders
* Added signals for order status changes