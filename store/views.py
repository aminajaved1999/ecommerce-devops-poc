from django.shortcuts import render, get_object_or_404
from .models import Product

# View 1: Home/Product List Page
def product_list(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'store/product_list.html', context)

# View 2: Product Detail Page
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product
    }
    return render(request, 'store/product_detail.html', context)

# View 3: Cart Page (Stub)
def view_cart(request):
    return render(request, 'store/cart.html')

# View 4: Checkout Page (Stub)
def checkout(request):
    return render(request, 'store/checkout.html')