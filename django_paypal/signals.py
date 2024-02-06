import django.dispatch

order_created = django.dispatch.Signal()
order_approved = django.dispatch.Signal()
order_captured = django.dispatch.Signal()
order_completed = django.dispatch.Signal()
