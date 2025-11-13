from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction # <-- Added for atomic transactions
import json

# Import all models
from .models import Product, Cart, CartItem, Order, OrderItem 

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

# View 2.5: Add to Cart Logic (Uses database CartItem)
def add_to_cart(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        cart = get_or_create_cart(request)
        
        try:
            quantity_to_add = int(request.POST.get('quantity', 1))
            if quantity_to_add < 1:
                quantity_to_add = 1
        except ValueError:
            quantity_to_add = 1
            
        # Get existing quantity in cart
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            current_cart_quantity = cart_item.quantity
        except CartItem.DoesNotExist:
            current_cart_quantity = 0

        total_new_quantity = current_cart_quantity + quantity_to_add

        # STOCK CHECK LOGIC
        if total_new_quantity > product.inventory_stock:
            messages.error(request, f"Cannot add {quantity_to_add} more. Only {product.inventory_stock - current_cart_quantity} of {product.name} are available in stock.")
            next_url = request.POST.get('next', 'product_list')
            return redirect(next_url)
            
        # Get or create the CartItem for this product in this cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': quantity_to_add}
        )

        if not created:
            # If item already exists, increase the quantity
            cart_item.quantity = total_new_quantity
            cart_item.save()

        messages.success(request, f"{quantity_to_add} x {product.name} added to cart!")
        
        # Check for 'next' URL to redirect after adding to cart
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
            product = Product.objects.get(pk=product_pk)
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except (Product.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'error': 'Item not found in cart'}, status=404)

        item_removed = False
        
        # STOCK CHECK FOR CART UPDATE
        if new_quantity > product.inventory_stock:
            # If requested quantity exceeds stock, limit it to available stock
            new_quantity = product.inventory_stock
            message = f"Warning: Quantity limited to available stock ({product.inventory_stock})"
        elif new_quantity > 0:
            message = 'Cart updated successfully.'
        else:
            message = 'Item removed successfully.'

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
            'message': message,
            'item_removed': item_removed,
            'new_quantity': new_quantity # Return new quantity for client-side update
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


# View 4: Checkout Page (Renders the confirmation form)
def checkout(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('product_list')
        
    context = {
        'cart_total': round(float(cart.total), 2)
    }
    return render(request, 'store/checkout.html', context)

# NEW: View to process the order (CREATE ORDER & DECREMENT STOCK)
@transaction.atomic # Ensures that all database operations succeed or fail together
def process_order(request):
    if request.method != 'POST':
        return redirect('checkout')

    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    if not cart_items:
        messages.error(request, "Cannot process order: Cart is empty.")
        return redirect('product_list')
        
    total_paid = cart.total
    
    # 1. Create the Order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_paid=total_paid,
        status='Processing'
    )
    
    # 2. Create OrderItems and Decrement Stock
    for cart_item in cart_items:
        product = cart_item.product
        
        # Check stock one last time (in a real app, this uses select_for_update)
        if product.inventory_stock < cart_item.quantity:
            # If stock is insufficient, raise an error and roll back the whole transaction
            raise Exception(f"Insufficient stock for {product.name}. Aborting order.")

        # Create OrderItem (capturing price at time of order)
        OrderItem.objects.create(
            order=order,
            product=product,
            price=product.price, 
            quantity=cart_item.quantity
        )
        
        # Decrement stock and save
        product.inventory_stock -= cart_item.quantity
        product.save()

    # 3. Clear the cart
    cart.items.all().delete()
    
    messages.success(request, f"Order #{order.id} successfully placed and stock has been reserved.")
    
    return redirect('order_success', order_id=order.id)

# NEW: Simple success page view
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    context = {
        'order': order
    }
    return render(request, 'store/order_success.html', context)