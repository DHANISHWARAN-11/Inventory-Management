# Generated by Django 5.2.3 on 2025-06-19 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_alter_item_description_alter_item_sku'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock_transaction',
            name='reference_note',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
