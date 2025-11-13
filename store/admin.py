from django.contrib import admin

# Register your models here.
from .models import Product, Cart, CartItem, Order, OrderItem # <-- Added new models

# Inline to display items within the Cart admin view
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)

# Inline to display items within the Order admin view
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)

# MODIFIED: Register Product with list_display to show stock
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'inventory_stock')
    list_editable = ('price', 'inventory_stock')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created_at', 'total')
    inlines = [CartItemInline]
    readonly_fields = ('total',)
    search_fields = ('user__username', 'session_key')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_paid', 'status')
    inlines = [OrderItemInline]
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'subtotal')
    list_filter = ('cart',)
    search_fields = ('product__name',)