from django.shortcuts import redirect, render
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from orders.forms import OrderForm
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def remove_cart_item(request, cart_item_id):
    try:
        cartItem = CartItem.objects.get(id=cart_item_id)
        cartItem.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')

def remove_cart(request, cart_item_id):
    cart = get_create_cart(request)
    try:
        cart_item = []
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                user=request.user,
                id=cart_item_id,
            )
        else:
            cart_item = CartItem.objects.get(
                cart=cart,
                id=cart_item_id,
            )
        cart_item.quantity -=1
        if cart_item.quantity <= 0:
            remove_cart_item(request, cart_item_id)
        else:
            cart_item.save()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')

def add_cart(request, product_id):
    variation_params={}
    selected_cart_item = None
    product = get_product_id(request, product_id)
    product_variation= get_variations_by_product(request, product) #un array de objetos Variation serian dos vlaores el category y el size
    ##crea el cart id que almacenara todos los cart items
    cart= get_create_cart(request)
    ##update cart items
    try:
        cart_item = []
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(
                user=request.user,
                product=product,
            )
        else:
            cart_item = CartItem.objects.filter(
                cart=cart,
                product=product,
            )
        for item in product_variation:
            variation_params[item.variation_category] = item.variation_value ## {'size': 'large', 'color':'red'}
        
        for item in cart_item:
            variation_match=0
            for variation in item.variations.all():    
                if variation_params[variation.variation_category] == variation.variation_value:
                    variation_match +=1
            if len(variation_params) == variation_match:
                selected_cart_item =item
                variation_match=0
         
        if not selected_cart_item: raise CartItem.DoesNotExist
        selected_cart_item.quantity +=1
        selected_cart_item.save()
    except CartItem.DoesNotExist:
        #create a new cart item
        cart_item = CartItem.objects.create(
            product = product,
            cart= cart,
            quantity= 1
        )
        if len(product_variation) > 0:
            cart_item.variations.clear()
            for item in product_variation:
                cart_item.variations.add(item)
        if request.user.is_authenticated:
            cart_item.user = request.user
            cart_item.save()
        else:
            cart_item.save()
    return redirect('cart')
 
def cart(request, quantity=0, total=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items= CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_items= CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            total +=  (item.product.price * item.quantity)
            quantity += item.quantity
    except Exception as e:
        pass
    context= {
        'quantity': quantity,
        'total_without_tax' : f"${total:.2f}",
        'total_tax': f"${((total*12)/100):.2f}",
        'total': f"${(((total*12)/100) + total):.2f}",
        'cart_items' :cart_items
    }
    return render(request, 'store/cart.html', context)

def get_variations_by_product(request, product):
    product_variation=[]
    if request.method == 'POST':
        for req in request.POST:
            key= req
            value = request.POST[key]
            try:
                variation = Variation.objects.filter(variation_category__iexact=key, product=product, variation_value__iexact=value)
                if len(variation) >0:
                    product_variation.append(variation.first())
            except Variation.DoesNotExist:
                pass
        
    return product_variation

def get_product_id(request, product_id):
    try:
        product = Product.objects.get(id= product_id)
    except Product.DoesNotExist:
        pass
    return product

def get_create_cart(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Exception as e:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    return cart

def getTotalQuanityTax(cart_items=[]):
    quantity=0
    subtotal=0
    for item in cart_items:
        subtotal +=  (item.product.price * item.quantity)
        quantity += item.quantity
    tax = ((subtotal * 12) / 100)
    subtotal = subtotal
    total = subtotal + tax  
    tax_str = '$' + f"{tax:.2f}"
    subtotal_str = '$' + f"{subtotal:.2f}"
    total_str = '$' + f"{total:.2f}"
    return { 'subtotal_str':subtotal_str, 'quantity': quantity, 'tax_str': tax_str, 'total_str': total_str, 'total': total, 'subtotal': subtotal, 'tax':tax}
@login_required
def checkout(request,  cart_items=None):
    prices= {}
    try:
        if request.user.is_authenticated:
            cart_items= CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_items= CartItem.objects.filter(cart=cart, is_active=True)
        print("cart items",cart_items)
        
    except Exception as e:
        pass
    prices = getTotalQuanityTax(cart_items)
    context= {
        'quantity': prices['quantity'],
        'total_without_tax' : prices['subtotal_str'],
        'total_tax': prices['tax_str'],
        'total': prices['total_str'],
        'cart_items' :cart_items,
        'form' : OrderForm()
    }
    if cart_items.count() <=0:
        return redirect('store')
    return render(request, 'store/checkout.html', context)

 