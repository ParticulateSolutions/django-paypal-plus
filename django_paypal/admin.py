from django.contrib import admin

from .models import PaypalPayment, PaypalTransaction, PaypalItem


class PaypalPaymentAdmin(admin.ModelAdmin):
    pass

admin.site.register(PaypalPayment, PaypalPaymentAdmin)


class PaypalTransactionAdmin(admin.ModelAdmin):
    pass

admin.site.register(PaypalTransaction, PaypalTransactionAdmin)


class PaypalItemAdmin(admin.ModelAdmin):
    pass

admin.site.register(PaypalItem, PaypalItemAdmin)
