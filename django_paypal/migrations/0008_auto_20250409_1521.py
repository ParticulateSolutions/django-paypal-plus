# Generated by Django 2.2.28 on 2025-04-09 13:21

from django.db import migrations


def migrate_capture_id(apps, schema_editor):
    """
    fill capture_id for all PaypalOrders
    """
    from django_paypal.api_types import OrderCaptureAPIResponse
    PaypalOrder = apps.get_model('django_paypal', 'PaypalOrder')
    for order in PaypalOrder.objects.all():
        if order.capture_id:
            continue
        
        for response in order.api_responses.filter(url__contains=f'/v2/checkout/orders/{order.order_id}/capture'):
            order_capture = OrderCaptureAPIResponse.from_dict(response.response_data)

            if order_capture.purchase_units:
                captures_id_list = []
                for purchase_unit in order_capture.purchase_units:
                    if purchase_unit.payments and purchase_unit.payments.captures:
                        for capture in purchase_unit.payments.captures:
                            if capture.id:
                                captures_id_list.append(capture.id)
                if captures_id_list:
                    order.capture_id = captures_id_list
                    order.save(update_fields=['capture_id'])
                    continue


class Migration(migrations.Migration):

    dependencies = [
        ('django_paypal', '0007_capture_id_for_direct_paypal_payment'),
    ]

    operations = [
        migrations.RunPython(migrate_capture_id, reverse_code=migrations.RunPython.noop, elidable=True),
    ]
