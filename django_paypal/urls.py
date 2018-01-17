from django.conf.urls import url

from .views import NotifyPaypalView

urlpatterns = [
    url(r'^notify/$', NotifyPaypalView.as_view(), name='notifiy'),
]
