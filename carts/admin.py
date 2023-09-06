from django.contrib import admin
from .models import CartItem, Cart
# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display= ('date_added', 'cart_id')
    
class CartItemAdmin(admin.ModelAdmin):
    list_display= ('product', 'cart', 'quantity', 'is_active')
    list_editable = ('is_active',)
    
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)