# Generated by Django 5.2.1 on 2025-05-29 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clotheshop', '0003_order_preferred_messenger'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='preferred_messenger',
            field=models.CharField(blank=True, default='neutral', max_length=20, null=True),
        ),
    ]
