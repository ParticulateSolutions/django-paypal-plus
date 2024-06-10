from requests import RequestException


class PaypalAuthFailure(RequestException):
    pass


class PaypalAPIError(RequestException):
    pass


class PaypalWebhookVerificationError(BaseException):
    pass


class PaypalOrderAlreadyCapturedError(RequestException):
    pass
