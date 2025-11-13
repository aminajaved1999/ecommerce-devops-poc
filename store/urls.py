from django.urls import path
from . import views

urlpatterns = [
    # Home/Product List
    path('', views.product_list, name='product_list'),

    # Product Detail
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.view_cart, name='cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
]