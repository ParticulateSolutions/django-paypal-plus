# Changelog

## v1.1.9
### Bugfixes and Changes
*   Corrected the data migration (from v1.1.7, fixed in v1.1.8) again to properly handle potentially missing `purchase_units`, `payments`, or `captures` fields within stored API response data when populating the `capture_id` field for existing orders.
*   Modified the `PaypalOrder.capture_id` model field to be non-nullable, ensuring it always defaults to an empty list (`default=list` instead of `null=True, default=list`). **Note:** This requires a database schema migration.
*   Updated the order capture logic (added in v1.1.5, refactored in v1.1.7) to safely handle optional `purchase_units`, `payments`, and `captures` attributes returned by the PayPal API, preventing potential errors.
*   Renamed the `Payments` dataclass to `PaymentCollection`. This dataclass now includes optional fields for `authorizations` and `refunds`, and the existing `captures` field was also made optional, reflecting the structure of PayPal API responses more accurately.
*   Performed general code cleanup, addressing potential type errors and improving overall robustness, particularly around handling potentially missing data in API responses.

---

## v1.1.8
### Bugfixes and Changes
*   Fixed the data migration introduced in v1.1.7. The migration previously failed because it incorrectly attempted to use a model method (`get_capture_api_responses`) within the migration environment. It now correctly filters associated `APIResponse` objects directly using `order.api_responses.filter(url__contains=...)`.

---

## v1.1.7
### Features
*   Introduced a data migration to populate the `capture_id` field (added in v1.1.5) for existing `PaypalOrder` records. This migration parses stored capture API responses to extract and save capture IDs.

### Bugfixes and Changes
*   Added the `payments` attribute (containing `captures`) to the `PurchaseUnit` API response dataclass.
*   Refactored the order capture logic to utilize the updated dataclass structure (specifically `purchase_unit.payments.captures`), improving consistency and type safety compared to the previous dictionary access.

---

## v1.1.6
### Bugfixes and Changes
*   Updated the database migration that added the `PaypalOrder.capture_id` field (from v1.1.5) to ensure compatibility with Django 2.2.

---

## v1.1.5
### Features
*   Added a new `capture_id` field (`JSONField`) to the `PaypalOrder` model. This field stores a list of capture IDs associated with the order, populated when the order is successfully captured via the API.

---

## v1.1.4
### Bugfixes and Changes
*   Made various fields across multiple API response dataclasses optional. This enhances robustness by preventing errors when the PayPal API response does not include certain expected fields.

---

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