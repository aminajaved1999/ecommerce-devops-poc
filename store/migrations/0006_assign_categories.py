from django.db import migrations

def assign_categories(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Category = apps.get_model('store', 'Category')

    # Create Categories
    clothing, _ = Category.objects.get_or_create(name="Clothing", defaults={'slug': 'clothing'})
    accessories, _ = Category.objects.get_or_create(name="Accessories", defaults={'slug': 'accessories'})
    footwear, _ = Category.objects.get_or_create(name="Footwear", defaults={'slug': 'footwear'})

    # Assign Categories to Products
    Product.objects.filter(name="Classic T-Shirt").update(category=clothing)
    Product.objects.filter(name="Leather Wallet").update(category=accessories)
    Product.objects.filter(name="Running Shoes").update(category=footwear)

class Migration(migrations.Migration):

    dependencies = [
        # *** FIX IS HERE: REPLACE THIS WITH THE ACTUAL NAME OF THE MIGRATION FILE ***
        ('store', '0005_category_product_category'), # <-- The dependency name MUST match the preceding model migration file name (without the .py)
    ]

    operations = [
        migrations.RunPython(assign_categories),
    ]