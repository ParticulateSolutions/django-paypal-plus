from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('django_paypal', '0006_auto_20240424_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='PaypalOrder',
            name='capture_id',
            field=models.JSONField(verbose_name='Capture ID', null=True, default=list),
        ),
    ]
