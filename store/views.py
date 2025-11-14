from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import json
from decimal import Decimal

# --- HARDCODED STATIC DATA ---
STATIC_PRODUCTS_DATA = [
    {'pk': 1, 'name': "Classic T-Shirt", 'description': "A comfortable 100% cotton t-shirt for year-round comfort.", 'price': 15.99, 'inventory_stock': 25, 'category': {'name': 'Clothing', 'slug': 'clothing'}},
    {'pk': 2, 'name': "Leather Wallet", 'description': "A stylish and durable leather wallet with RFID protection.", 'price': 29.99, 'inventory_stock': 15, 'category': {'name': 'Accessories', 'slug': 'accessories'}},
    {'pk': 3, 'name': "Running Shoes", 'description': "Lightweight performance shoes designed for your daily run, featuring high-grip soles.", 'price': 79.99, 'inventory_stock': 20, 'category': {'name': 'Footwear', 'slug': 'footwear'}},
    {'pk': 4, 'name': "Slim Fit Hoodie", 'description': "A lightweight, modern slim-fit hoodie perfect for layering.", 'price': 45.50, 'inventory_stock': 12, 'category': {'name': 'Clothing', 'slug': 'clothing'}},
    {'pk': 5, 'name': "Cross-Body Bag", 'description': "A compact and versatile cross-body bag for essentials and travel.", 'price': 35.00, 'inventory_stock': 18, 'category': {'name': 'Accessories', 'slug': 'accessories'}},
    {'pk': 6, 'name': "Business Loafers", 'description': "Classic leather loafers suitable for formal and business casual wear.", 'price': 120.00, 'inventory_stock': 8, 'category': {'name': 'Footwear', 'slug': 'footwear'}},
    {'pk': 7, 'name': "Premium Denim Jeans", 'description': "Durable and comfortable premium denim jeans with a modern fit.", 'price': 59.99, 'inventory_stock': 10, 'category': {'name': 'Clothing', 'slug': 'clothing'}},
]

# --- MOCK CLASSES TO MIMIC DJANGO MODEL BEHAVIOR ---
class MockProduct:
    def __init__(self, data):
        for k, v in data.items():
            setattr(self, k, v)
        # Mock Category object for product_list.html template needs
        self.category = type('MockCategory', (object,), data.get('category', {'name': 'Unknown', 'slug': 'unknown'}))()

class MockCartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity
        # Mimic CartItem subtotal calculation
        self.subtotal = round(product.price * quantity, 2)
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# --- SESSION UTILITIES ---
def get_session_cart(session):
    """Initializes cart data structure in session if not present: {product_pk: quantity}."""
    if 'cart' not in session:
        session['cart'] = {} 
    return session['cart']

def get_cart_items_for_template(session):
    """Converts session data into a list of MockCartItem objects for rendering."""
    cart_items_data = get_session_cart(session)
    items = []
    total = 0.0

    # Retrieve full product details from static data
    product_map = {p['pk']: MockProduct(p) for p in STATIC_PRODUCTS_DATA}
    
    for pk_str, quantity in cart_items_data.items():
        try:
            pk = int(pk_str)
        except ValueError:
            continue
            
        if pk in product_map and quantity > 0:
            product = product_map[pk]
            item = MockCartItem(product, quantity)
            items.append(item)
            total += item.subtotal
            
    return items, round(total, 2)

# -------------------------- VIEWS --------------------------

# View 1: Home/Product List Page (Uses Static Data)
def product_list(request, category_slug=None):
    current_category = None
    
    products_data = [MockProduct(data) for data in STATIC_PRODUCTS_DATA]
    
    if category_slug:
        products = [p for p in products_data if p.category.slug == category_slug]
        
        category_item = next((p.category for p in products if p.category.slug == category_slug), None)
        if category_item:
            current_category = category_item.name
    else:
        products = products_data

    context = {
        'products': products,
        'current_category': current_category
    }
    return render(request, 'store/product_list.html', context)

# View 2: Product Detail Page (Uses Static Data)
def product_detail(request, pk):
    product_data = next((item for item in STATIC_PRODUCTS_DATA if item['pk'] == pk), None)
    
    if product_data is None:
        return redirect('product_list')

    product = MockProduct(product_data)
    
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)

# View 2.5: Add to Cart Logic (Uses Session)
def add_to_cart(request, pk):
    if request.method == 'POST':
        product_data = next((item for item in STATIC_PRODUCTS_DATA if item['pk'] == pk), None)
        if not product_data:
            messages.error(request, "Product not found.")
            return redirect('product_list')

        cart = get_session_cart(request.session)
        product_pk_str = str(pk)
        
        try:
            quantity_to_add = int(request.POST.get('quantity', 1))
            if quantity_to_add < 1:
                quantity_to_add = 1
        except ValueError:
            quantity_to_add = 1
            
        current_cart_quantity = cart.get(product_pk_str, 0)
        total_new_quantity = current_cart_quantity + quantity_to_add

        inventory_stock = product_data['inventory_stock']
        if total_new_quantity > inventory_stock:
            messages.error(request, f"Cannot add {quantity_to_add} more. Only {inventory_stock - current_cart_quantity} of {product_data['name']} are available in stock.")
            next_url = request.POST.get('next', 'product_list')
            return redirect(next_url)
            
        cart[product_pk_str] = total_new_quantity
        request.session.modified = True 

        messages.success(request, f"{quantity_to_add} x {product_data['name']} added to cart!")
        
        next_url = request.POST.get('next', 'cart')
        return redirect(next_url)

# View 3.5: Update Cart Logic (Session-based AJAX)
def update_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_pk = int(data.get('product_id'))
            new_quantity = int(data.get('quantity', 0))
            product_pk_str = str(product_pk)
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({'error': 'Invalid request data'}, status=400)
        
        cart = get_session_cart(request.session)
        
        product_data = next((item for item in STATIC_PRODUCTS_DATA if item['pk'] == product_pk), None)
        if not product_data:
             return JsonResponse({'error': 'Item not found.'}, status=404)
        
        inventory_stock = product_data['inventory_stock']
        item_removed = False
        message = 'Cart updated successfully.'
        item_subtotal = 0.0

        if new_quantity > inventory_stock:
            new_quantity = inventory_stock
            message = f"Warning: Quantity limited to available stock ({inventory_stock})"
        
        if new_quantity > 0:
            cart[product_pk_str] = new_quantity
            item_subtotal = Decimal(product_data['price']) * new_quantity
        else:
            if product_pk_str in cart:
                del cart[product_pk_str]
                item_removed = True
                message = 'Item removed successfully.'
            
        request.session.modified = True

        _, cart_total = get_cart_items_for_template(request.session)

        return JsonResponse({
            'success': True,
            'item_subtotal': round(float(item_subtotal), 2),
            'cart_total': cart_total,
            'message': message,
            'item_removed': item_removed,
            'new_quantity': new_quantity
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# View 3: Cart Page (Uses Session)
def view_cart(request):
    cart_items, cart_total = get_cart_items_for_template(request.session)
        
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total
    }
    
    return render(request, 'store/cart.html', context)


# View 4: Checkout Page (Uses Session, Redirects Order Processing)
def checkout(request):
    cart_items, cart_total = get_cart_items_for_template(request.session)
    
    if not cart_items:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('product_list')
        
    context = {'cart_total': cart_total}
    return render(request, 'store/checkout.html', context)

# View to process the order (MOCK SUCCESS)
def process_order(request):
    messages.success(request, "Order processed successfully! (Note: Stock/Order persistence is disabled for free tier PoC).")
    # Redirect to mock order ID
    return redirect('order_success', order_id=999)

# Simple success page view (MOCK DATA)
def order_success(request, order_id):
    # Retrieve mock cart for display before clearing
    cart_items, cart_total = get_cart_items_for_template(request.session)
    
    # Clear the session cart to simulate completion
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True

    # Mock Order object for template rendering
    mock_order = type('MockOrder', (object,), {
        'id': order_id, 
        'total_paid': cart_total, 
        'status': 'Completed (PoC)',
        'created_at': 'N/A',
        'items': type('MockOrderItems', (object,), {'count': lambda: len(cart_items)})()
    })

    context = {'order': mock_order}
    return render(request, 'store/order_success.html', context)