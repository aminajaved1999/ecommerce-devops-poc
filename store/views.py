from django.shortcuts import render

# Create your views here.
from .models import Product

# Create your views here.
def product_list(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'store/product_list.html', context)