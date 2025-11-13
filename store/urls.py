from django.urls import path
from . import views

urlpatterns = [
    # Home/Product List (Modified to accept optional category slug)
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'), # <-- NEW: Filtered view

    # Product Detail
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Add to Cart functionality
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),

    # Cart
    path('cart/', views.view_cart, name='cart'),
    
    # AJAX Cart Update
    path('update_cart/', views.update_cart, name='update_cart'), 

    # Checkout and Order Processing
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_order, name='process_order'), 
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
]