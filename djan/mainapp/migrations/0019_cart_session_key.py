# Generated by Django 5.1.3 on 2025-01-11 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0018_remove_cart_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='session_key',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
