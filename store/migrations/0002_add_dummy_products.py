from django.db import migrations

def create_dummy_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    
    # 1. Define all products with their data, including the inventory_stock value you want to keep.
    products_to_create = [
        {"name": "Classic T-Shirt", "description": "A comfortable 100% cotton t-shirt for year-round comfort.", "price": 15.99, "inventory_stock": 25},
        {"name": "Leather Wallet", "description": "A stylish and durable leather wallet with RFID protection.", "price": 29.99, "inventory_stock": 15},
        {"name": "Running Shoes", "description": "Lightweight performance shoes designed for your daily run, featuring high-grip soles.", "price": 79.99, "inventory_stock": 20},
        {"name": "Slim Fit Hoodie", "description": "A lightweight, modern slim-fit hoodie perfect for layering.", "price": 45.50, "inventory_stock": 12},
        {"name": "Cross-Body Bag", "description": "A compact and versatile cross-body bag for essentials and travel.", "price": 35.00, "inventory_stock": 18},
        {"name": "Business Loafers", "description": "Classic leather loafers suitable for formal and business casual wear.", "price": 120.00, "inventory_stock": 8},
        {"name": "Premium Denim Jeans", "description": "Durable and comfortable premium denim jeans with a modern fit.", "price": 59.99, "inventory_stock": 10},
    ]

    # 2. Critical Check: Determine if the historical model (at this point in time) has the field.
    # This prevents the TypeError.
    has_inventory_stock = 'inventory_stock' in [f.name for f in Product._meta.fields]

    for product_data in products_to_create:
        create_kwargs = {
            'name': product_data['name'],
            'description': product_data['description'],
            'price': product_data['price'],
        }
        
        # 3. Only pass the argument if the field exists on the current model state.
        if has_inventory_stock:
            create_kwargs['inventory_stock'] = product_data['inventory_stock']

        Product.objects.create(**create_kwargs)

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_dummy_products),
    ]