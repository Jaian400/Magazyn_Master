# Generated by Django 5.1.3 on 2025-01-11 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0016_warehouseproduct_product_price_discounted'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='session_uuid',
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
    ]
