from django.db import models
from django.urls import reverse
from store.models import Product, Variation

# Create your models here.
class Cart(models.Model):
    cart_id= models.CharField(max_length=250, blank=True)
    date_added=models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart= models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity =models.IntegerField()
    is_active = models.BooleanField(default=True)
    variations= models.ManyToManyField(Variation, blank=True)
    
    def get_price(self):
        total_item_price = f"${(self.quantity * self.product.price):.2f}" 
        return total_item_price

    def __str__(self):
        return self.product.product_name

    