from django.db import migrations
try:
    # Django 3.1 and newer
    from django.db.models import JSONField
except ImportError:
    # Django 2.2
    from django.contrib.postgres.fields import JSONField


class Migration(migrations.Migration):

    dependencies = [
        ('django_paypal', '0006_auto_20240424_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='PaypalOrder',
            name='capture_id',
            field=JSONField(verbose_name='Capture ID', null=True, default=list),
        ),
    ]
