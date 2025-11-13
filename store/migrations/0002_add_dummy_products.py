from django.db import migrations

def create_dummy_products(apps, schema_editor):
    """
    Creates dummy products for the e-commerce PoC.
    """
    Product = apps.get_model('store', 'Product')

    Product.objects.create(
        name="Classic T-Shirt",
        description="A comfortable 100% cotton t-shirt.",
        price=15.99
    )
    Product.objects.create(
        name="Leather Wallet",
        description="A stylish and durable leather wallet.",
        price=29.99
    )
    Product.objects.create(
        name="Running Shoes",
        description="Lightweight shoes for your daily run.",
        price=79.99
    )

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'), # This name might be different, check your 0001 file
    ]

    operations = [
        migrations.RunPython(create_dummy_products),
    ]