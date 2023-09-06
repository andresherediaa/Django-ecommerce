from .models import Cart, CartItem
from .views import _cart_id

def count_items(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    items_number = CartItem.objects.all().filter(cart=cart)
    number_items = 0
    for item in items_number:
        number_items += item.quantity
    return dict(number_items=number_items)