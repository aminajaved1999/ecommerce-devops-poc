from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
import json # <-- Added to handle JSON data

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

# View 2.5: Add to Cart Logic (Handles POST request)
def add_to_cart(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1
            
        cart = request.session.get('cart', {})
        product_pk_str = str(pk)
        
        if product_pk_str in cart:
            cart[product_pk_str]['quantity'] += quantity
        else:
            cart[product_pk_str] = {
                'product_id': pk,
                'name': product.name,
                'price': str(product.price),
                'quantity': quantity,
            }

        request.session['cart'] = cart
        request.session.modified = True
        
        messages.success(request, f"{quantity} x {product.name} added to cart!")
        
    return redirect('cart')

# NEW View 3.5: Update Cart Logic (Modified for AJAX)
def update_cart(request):
    # This view must handle a POST request containing JSON data
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_pk_str = str(data.get('product_id'))
            new_quantity = int(data.get('quantity', 0))
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({'error': 'Invalid request data'}, status=400)

        cart = request.session.get('cart', {})
        
        if product_pk_str in cart:
            if new_quantity > 0:
                cart[product_pk_str]['quantity'] = new_quantity
            else:
                # Remove item if quantity is zero
                del cart[product_pk_str]
                
            request.session['cart'] = cart
            request.session.modified = True
        
        # Recalculate cart total and get updated item data
        cart_total = 0.0
        item_subtotal = 0.0
        
        # Recalculate to ensure accurate response data
        for item_pk, item_data in cart.items():
            price = float(item_data['price'])
            quantity = item_data['quantity']
            subtotal = price * quantity
            
            cart_total += subtotal
            
            # Store the subtotal for the item just updated
            if item_pk == product_pk_str:
                item_subtotal = subtotal
        
        # Return new totals as JSON
        return JsonResponse({
            'success': True,
            'item_subtotal': round(item_subtotal, 2),
            'cart_total': round(cart_total, 2),
            'message': 'Cart updated successfully.',
            'item_removed': new_quantity <= 0 and product_pk_str not in cart # Check for item removal
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# View 3: Cart Page (Unchanged)
def view_cart(request):
    cart = request.session.get('cart', {})
    
    # Reconstruct cart items for display and calculate total
    cart_items = []
    cart_total = 0.0
    
    for item_pk, item_data in cart.items():
        price = float(item_data['price'])
        quantity = item_data['quantity']
        subtotal = price * quantity
        
        cart_total += subtotal
        
        cart_items.append({
            'product_id': int(item_pk),
            'name': item_data['name'],
            'price': price,
            'quantity': quantity,
            'subtotal': subtotal,
        })
        
    context = {
        'cart_items': cart_items,
        'cart_total': round(cart_total, 2)
    }
    
    return render(request, 'store/cart.html', context)


# View 4: Checkout Page (Stub)
def checkout(request):
    return render(request, 'store/checkout.html')