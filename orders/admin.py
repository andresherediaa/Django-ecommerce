from django.contrib import admin
from .models import Payment, Order, OrderProduct

class PaymentAdmin(admin.ModelAdmin):
  list_display = ('user', 'payment_method', 'amount_paid', 'payment_id', 'status', 'created_at')
  
class OrderAdmin(admin.ModelAdmin):
  list_display = (
    'user',
    'payment',
    'order_number',
    'first_name',
    'last_name',
    'phone',
    'email',
    'address_line_1',
    'address_line_2',
    'country',
    'state',
    'city',
    'order_note',
    'order_total',
    'tax',
    'status',
    'ip',
    'is_ordered',
    'created_at',
    'updated_at',
)
  
class OrderProductAdmin(admin.ModelAdmin):
  list_display = (
    'order',
    'payment',
    'user',
    'product',
    'variation',
    'color',
    'size',
    'quantity',
    'product_price',
    'ordered',
    'created_at',
    'updated_at',
)
  
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
