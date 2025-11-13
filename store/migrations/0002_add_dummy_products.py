from django.db import migrations

def create_dummy_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')

    # Original Products - Stock increased for better demo
    Product.objects.create(
        name="Classic T-Shirt",
        description="A comfortable 100% cotton t-shirt for year-round comfort.",
        price=15.99,
        inventory_stock=25
    )
    Product.objects.create(
        name="Leather Wallet",
        description="A stylish and durable leather wallet with RFID protection.",
        price=29.99,
        inventory_stock=15
    )
    Product.objects.create(
        name="Running Shoes",
        description="Lightweight performance shoes designed for your daily run, featuring high-grip soles.",
        price=79.99,
        inventory_stock=20
    )
    
    # NEW PRODUCTS ADDED:
    Product.objects.create(
        name="Slim Fit Hoodie",
        description="A lightweight, modern slim-fit hoodie perfect for layering.",
        price=45.50,
        inventory_stock=12
    )
    Product.objects.create(
        name="Cross-Body Bag",
        description="A compact and versatile cross-body bag for essentials and travel.",
        price=35.00,
        inventory_stock=18
    )
    Product.objects.create(
        name="Business Loafers",
        description="Classic leather loafers suitable for formal and business casual wear.",
        price=120.00,
        inventory_stock=8
    )
    Product.objects.create(
        name="Premium Denim Jeans",
        description="Durable and comfortable premium denim jeans with a modern fit.",
        price=59.99,
        inventory_stock=10
    )


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'), # This is now correct!
    ]

    operations = [
        migrations.RunPython(create_dummy_products),
    ]