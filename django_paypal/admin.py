from django.contrib import admin

from .models import PaypalOrder, PaypalAPIResponse


class PaypalOrderAdmin(admin.ModelAdmin):
    pass


admin.site.register(PaypalOrder, PaypalOrderAdmin)


class PaypalAPIResponseAdmin(admin.ModelAdmin):
    pass


admin.site.register(PaypalAPIResponse, PaypalAPIResponseAdmin)
