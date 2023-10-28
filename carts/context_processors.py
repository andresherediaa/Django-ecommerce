from .models import Cart, CartItem
from .views import _cart_id

def count_items(request):
    items_number = []
    try:
        cart = Cart.objects.filter(cart_id=_cart_id(request))
        if request.user.is_authenticated:
            items_number = CartItem.objects.all().filter(user=request.user)
        else:
            items_number = CartItem.objects.all().filter(cart=cart[:1])
    except Cart.DoesNotExist:
        items_number = []
    
    number_items = 0
    for item in items_number:
        number_items += item.quantity
    return dict(number_items=number_items)