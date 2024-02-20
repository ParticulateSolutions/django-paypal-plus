# Changelog

## v1.0.0

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