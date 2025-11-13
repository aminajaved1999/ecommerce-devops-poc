from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
import json

# Import all models, including the new ones
from .models import Product, Cart, CartItem 

# --- Helper function to get the user's cart object ---
def get_or_create_cart(request):
    if request.user.is_authenticated:
        # For logged-in users, try to find a cart linked to the user
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For anonymous users, use the session key
        session_key = request.session.session_key
        if not session_key:
            # Must ensure a session key exists before creating an anonymous cart
            request.session.create()
            session_key = request.session.session_key
            
        # The unique=True constraint on session_key in the model guarantees this is safe
        cart, created = Cart.objects.get_or_create(session_key=session_key)

    # If the user logs in while having an anonymous cart, merge the carts (future improvement)
    # For now, this simple logic ensures a cart is always returned.
    return cart

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

# View 2.5: Add to Cart Logic (Uses database CartItem) - MODIFIED
def add_to_cart(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        cart = get_or_create_cart(request)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1
            
        # Get or create the CartItem for this product in this cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # If item already exists, increase the quantity
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, f"{quantity} x {product.name} added to cart!")
        
        # NEW LOGIC: Check for 'next' URL to redirect after adding to cart
        next_url = request.POST.get('next', 'cart')
        return redirect(next_url)

# View 3.5: Update Cart Logic (Uses database CartItem and AJAX)
def update_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_pk = int(data.get('product_id'))
            new_quantity = int(data.get('quantity', 0))
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({'error': 'Invalid request data'}, status=400)

        cart = get_or_create_cart(request)
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product__pk=product_pk)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found in cart'}, status=404)

        item_removed = False
        
        if new_quantity > 0:
            # Update quantity
            cart_item.quantity = new_quantity
            cart_item.save()
            item_subtotal = cart_item.subtotal
        else:
            # Remove item if quantity is zero
            cart_item.delete()
            item_removed = True
            item_subtotal = 0.0
            
        # Recalculate cart total using the Cart model's property
        cart_total = cart.total if not item_removed else get_or_create_cart(request).total

        # Return new totals as JSON
        return JsonResponse({
            'success': True,
            'item_subtotal': round(float(item_subtotal), 2),
            'cart_total': round(float(cart_total), 2),
            'message': 'Cart updated successfully.',
            'item_removed': item_removed
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# View 3: Cart Page (Now functional, querying database CartItems)
def view_cart(request):
    cart = get_or_create_cart(request)
    
    # Get all items related to the cart
    cart_items = cart.items.select_related('product').all()
    cart_total = cart.total
        
    context = {
        # Pass the database-backed CartItem objects directly to the template
        'cart_items': cart_items,
        'cart_total': round(float(cart_total), 2)
    }
    
    return render(request, 'store/cart.html', context)


# View 4: Checkout Page (Stub)
def checkout(request):
    return render(request, 'store/checkout.html')