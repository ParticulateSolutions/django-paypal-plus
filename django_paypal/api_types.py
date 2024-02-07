from dataclasses import dataclass
from typing import Optional, List, Literal, NamedTuple, Dict, Any
from dataclass_wizard import JSONWizard

ItemCategories = Literal['DIGITAL_GOODS', 'PHYSICAL_GOODS', 'DONATION']
ShippingType = Literal['SHIPPING', 'PICKUP_IN_PERSON', 'PICKUP_IN_STORE', 'PICKUP_FROM_PERSON']
CardType = Literal[
    'VISA',
    'MASTERCARD',
    'DISCOVER',
    'AMEX',
    'SOLO',
    'JCB',
    'STAR',
    'DELTA',
    'SWITCH',
    'MAESTRO',
    'CB_NATIONALE',
    'CONFIGOGA',
    'CONFIDIS',
    'ELECTRON',
    'CETELEM',
    'CHINA_UNION_PAY',
]


@dataclass
class OAuthResponse:
    scope: str
    access_token: str
    token_type: str
    app_id: str
    expires_in: int
    nonce: str


@dataclass
class PhoneNumber:
    national_number: str


@dataclass
class Phone:
    phone_number: PhoneNumber
    phone_type: Optional[Literal['FAX', 'HOME', 'MOBILE', 'OTHER', 'PAGER']] = None


@dataclass
class AccountHolder:
    given_name: Optional[str] = None
    surname: Optional[str] = None
    full_name: Optional[str] = None

    def __post_init__(self):
        if self.given_name and len(self.given_name) > 140:
            raise ValueError('Given name must be 140 characters or fewer')
        if self.surname and len(self.surname) > 140:
            raise ValueError('Surname must be 140 characters or fewer')


@dataclass
class ExperienceContext:
    brand_name: Optional[str] = None
    shipping_preference: Optional[Literal['GET_FROM_FILE', 'NO_SHIPPING', 'SET_PROVIDED_ADDRESS']] = None
    landing_page: Optional[Literal['LOGIN', 'GUEST_CHECKOUT', 'NO_PREFERENCE']] = None
    user_action: Optional[Literal['CONTINUE', 'PAY_NOW']] = None
    payment_method_preference: Optional[Literal['UNRESTRICTED', 'IMMEDIATE_PAYMENT_REQUIRED']] = None
    locale: Optional[str] = None
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None


@dataclass
class TaxInfo:
    tax_id: Optional[str] = None
    tax_id_type: Optional[str] = None


@dataclass
class Address:
    country_code: str
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    admin_area_1: Optional[str] = None
    admin_area_2: Optional[str] = None
    postal_code: Optional[str] = None


@dataclass
class Customer:
    id: Optional[str] = None
    email_address: Optional[str] = None
    phone: Optional[Phone] = None


@dataclass
class Vault:
    usage_type: str
    store_in_vault: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None
    customer_type: Optional[str] = None
    permit_multiple_payment_tokens: Optional[bool] = None


@dataclass
class Attributes:
    customer: Optional[Customer] = None
    vault: Optional[Vault] = None


@dataclass
class PayPal:
    experience_context: Optional[ExperienceContext] = None
    billing_agreement_id: Optional[str] = None
    vault_id: Optional[str] = None
    email_address: Optional[str] = None
    birth_date: Optional[str] = None
    tax_info: Optional[TaxInfo] = None
    address: Optional[Address] = None
    attributes: Optional[Attributes] = None


@dataclass
class PaymentSource(JSONWizard):
    class _(JSONWizard.Meta):
        key_transform_with_dump = 'SNAKE'

    paypal: PayPal


@dataclass
class Amount:
    currency_code: str
    value: str


@dataclass
class Tax:
    currency_code: str
    value: str


@dataclass
class PurchaseItem:
    name: str
    quantity: int
    category: ItemCategories
    unit_amount: Amount
    description: Optional[str] = None
    sku: Optional[str] = None
    tax: Optional[Tax] = None


@dataclass
class Breakdown:
    item_total: Optional[Amount] = None
    shipping: Optional[Amount] = None
    handling: Optional[Amount] = None
    tax_total: Optional[Amount] = None
    shipping_discount: Optional[Amount] = None
    discount: Optional[Amount] = None


@dataclass
class PurchaseUnitAmount(Amount):
    breakdown: Optional[Breakdown] = None


@dataclass
class Payee:
    email_address: Optional[str] = None
    merchant_id: Optional[str] = None


@dataclass
class PlatformFees:
    amount: Optional[Amount]
    payee_pricing_tier_id: Optional[str] = None
    payee_receivable_fx_rate_id: Optional[str] = None
    disbursement_mode: Optional[Literal['INSTANT', 'DELAYED']] = None


@dataclass
class PaymentInstruction:
    platform_fees: Optional[PlatformFees] = None


@dataclass
class ShippingOption:
    id: str
    label: str
    selected: bool
    type: ShippingType
    amount: Optional[Amount] = None


@dataclass
class Shipping:
    type: ShippingType = None
    options: Optional[List[ShippingOption]] = None
    name: Optional[AccountHolder] = None
    address: Optional[Address] = None


@dataclass
class Level2Data:
    invoice_id: Optional[str] = None
    tax_total: Optional[Amount] = None


@dataclass
class LineItem:
    name: str
    quantity: int
    unit_amount: Amount
    description: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[ItemCategories] = None
    tax: Optional[Amount] = None
    commodity_code: Optional[str] = None
    unit_of_measure: Optional[str] = None
    discount_amount: Optional[Amount] = None
    total_amount: Optional[Amount] = None


@dataclass
class Level3Data:
    ships_from_postal_code: Optional[str] = None
    line_items: Optional[List[LineItem]] = None
    shipping_amount: Optional[Amount] = None
    duty_amount: Optional[Amount] = None
    discount_amount: Optional[Amount] = None
    address: Optional[Address] = None


@dataclass
class SupplementaryCardData:
    level_2: Optional[Level2Data] = None
    level_3: Optional[Level3Data] = None


@dataclass
class SupplementaryData:
    card: SupplementaryCardData


@dataclass
class PurchaseUnit(JSONWizard):
    class _(JSONWizard.Meta):
        key_transform_with_dump = 'SNAKE'

    amount: PurchaseUnitAmount
    reference_id: Optional[str] = None
    description: Optional[str] = None
    custom_id: Optional[str] = None
    invoice_id: Optional[str] = None
    soft_descriptor: Optional[str] = None
    items: Optional[List[PurchaseItem]] = None
    payee: Optional[Payee] = None
    payment_instruction: Optional[PaymentInstruction] = None
    shipping: Optional[Shipping] = None
    supplementary_data: Optional[SupplementaryData] = None


@dataclass
class PreviousNetworkTransactionReference:
    id: str
    network: CardType
    date: Optional[str] = None
    acquirer_reference_number: Optional[str] = None


@dataclass
class StoredPaymentSource:
    payment_initiator: Literal['CUSTOMER', 'MERCHANT']
    payment_type: Literal['ONE_TIME', 'RECURRING', 'UNSCHEDULED']
    usage: Optional[Literal['FIRST', 'SUBSEQUENT', 'DERIVED']] = None
    previous_network_transaction_reference: Optional[PreviousNetworkTransactionReference] = None


@dataclass
class ApplicationContext(JSONWizard):
    class _(JSONWizard.Meta):
        key_transform_with_dump = 'SNAKE'

    stored_payment_source: StoredPaymentSource


class APIAuthCredentials(NamedTuple):
    client_id: str
    client_secret: str


@dataclass
class Link:
    href: str
    method: Literal['GET', 'POST', 'PATCH', 'DELETE']
    rel: str


@dataclass
class OrderCreatedAPIResponse(JSONWizard):
    class _(JSONWizard.Meta):
        key_transform_with_dump = 'SNAKE'

    id: str
    links: List[Link]
    payment_source: PaymentSource
    status: str


@dataclass
class Payer:
    payer_id: str
    address: Optional[Address] = None
    email_address: Optional[str] = None
    name: Optional[AccountHolder] = None


@dataclass
class OrderDetailPayPal:
    account_id: str
    account_status: str
    address: Address
    email_address: str
    name: AccountHolder


@dataclass
class OrderDetailPaymentSource:
    paypal: OrderDetailPayPal


@dataclass
class OrderDetailAPIResponse(JSONWizard):
    class _(JSONWizard.Meta):
        key_transform_with_dump = 'SNAKE'

    id: str
    create_time: str
    links: List[Link]
    payer: Payer
    payment_source: OrderDetailPaymentSource
    purchase_units: List[PurchaseUnit]
    status: str


@dataclass
class SellerProtection:
    dispute_categories: List[str]
    status: str


@dataclass
class SellerReceivableBreakdown:
    gross_amount: Amount
    net_amount: Amount
    paypal_fee: Amount


@dataclass
class Capture:
    amount: Amount
    create_time: str
    final_capture: bool
    id: str
    links: List[Link]
    seller_protection: SellerProtection
    seller_receivable_breakdown: SellerReceivableBreakdown
    status: str
    update_time: str


@dataclass
class Payments:
    captures: List[Capture]


@dataclass
class CaptureAddress:
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    admin_area_1: Optional[str] = None
    admin_area_2: Optional[str] = None
    postal_code: Optional[str] = None


@dataclass
class CaptureShipping:
    address: CaptureAddress
    name: AccountHolder


@dataclass
class CapturedPurchaseUnit:
    payments: Payments
    reference_id: str
    shipping: CaptureShipping


@dataclass
class OrderCaptureAPIResponse(JSONWizard):
    class _(JSONWizard.Meta):
        key_transform_with_dump = 'SNAKE'

    id: str
    links: List[Link]
    payer: Payer
    payment_source: OrderDetailPaymentSource
    purchase_units: List[CapturedPurchaseUnit]
    status: str


class WebhookEvent(NamedTuple):
    create_time: str
    event_type: str
    event_version: str
    id: str
    links: List[Link]
    resource: Dict[str, Any]
    resource_type: str
    resource_version: str
    summary: str


@dataclass
class SellerReceivableBreakdown:
    gross_amount: Amount
    net_amount: Amount
    paypal_fee: Amount


@dataclass
class SellerProtection:
    dispute_categories: List[str]
    status: str


@dataclass
class Capture:
    amount: Amount
    create_time: str
    final_capture: bool
    id: str
    links: List[Link]
    seller_protection: SellerProtection
    seller_receivable_breakdown: SellerReceivableBreakdown
    status: str
    update_time: str
