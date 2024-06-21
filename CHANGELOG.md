# Changelog

## v1.1.3
### Bugfixes and Changes

#### Refactor: Literals & Constants
- Added `Intent`, `ProcessingInstruction`, and `PhoneType` as `Literal` types.

#### Link Class Updates
- Moved `Link` class definition up and added `Optional` typing for the `method` attribute.

#### PhoneNumber Enhancements
- Added `extension_number` attribute to `PhoneNumber`.

#### Class Renaming and Modifications
- Renamed `Phone` to `PhoneWithType`.
- Renamed `AccountHolder` to `Name` and updated with additional attributes: `prefix`, `middle_name`, and `suffix`.

#### Address Enhancements
- Added `AddressDetails` class for detailed address components.
- Extended `Address` class with additional attributes: `address_line_3`, `admin_area_3`, `admin_area_4`, and `address_details`.

#### Customer Class Update
- Added `merchant_customer_id` attribute to `Customer`.

#### PayPalWallet and Attributes
- Renamed `PayPal` to `PayPalWallet`.
- Renamed `Attributes` to `PayPalWalletAttributes`.
- Introduced `PayPalWalletResponse` for response handling.

#### Shipping Detail Updates
- Renamed `Shipping` to `ShippingDetail`.
- Introduced `ShippingWithTrackingDetail`, incorporating tracking capabilities with `Tracker` and `TrackerItem` classes.

#### PurchaseItem Class Updates
- Made `category` attribute optional.

#### PurchaseUnit Modifications
- Made `amount` attribute optional in `PurchaseUnit`.

#### Order Response Updates
- Introduced `PaymentSourceResponse` class.
- Updated `OrderDetailAPIResponse` with additional optional attributes: `update_time`, `processing_instruction`, and `intent`.
- `OrderCaptureAPIResponse` now extends from `OrderDetailAPIResponse`.

#### Error Handling
- When capturing order and receiving an API error that does not lead to `PaypalOrderAlreadyCapturedError` no error was raised.
This now raises `PaypalAPIError` again.

### Removals

#### Deprecated Classes
- Removed `CETELEM` and `CHINA_UNION_PAY`.

#### Removed Unused Data Classes
- `CaptureAddress`, `CaptureShipping`, and `CapturedPurchaseUnit`.

These changes introduce enhanced flexibility and more detailed data structures, ensuring comprehensive handling of various attributes and improving code readability and maintainability.

---

## v1.1.2
### Bugfixes
* When paying with PayPal, but without an account (i.e. credit card), a shipping address might not exist in PayPal's capture response.
This threw an error when capturing while still successfuly capturing the order on PayPal's side. This field is now optional
* When capturing an order that has been captured/completed already, we now throw a `PaypalOrderAlreadyCapturedError` exception

---

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