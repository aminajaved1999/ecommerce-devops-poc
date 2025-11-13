from django.urls import path
from . import views

urlpatterns = [
    # Home/Product List
    path('', views.product_list, name='product_list'),

    # Product Detail
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Add to Cart functionality
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),

    # Cart
    path('cart/', views.view_cart, name='cart'),
    
    # NEW: Update Cart functionality (for quantity changes)
    path('update_cart/', views.update_cart, name='update_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
]