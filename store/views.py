from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.views import add_cart, _cart_id
from carts.models import CartItem, Cart
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product
from django.http import HttpResponse

def listing(request, products):
    paginator= Paginator(products, 3)
    page_number = request.GET.get("page")
    page_number = int(page_number) if page_number and page_number.isdigit() else 1
    page_products = paginator.get_page(page_number)
    return {'page_number':page_number, 'page_products':page_products, 'paginator':paginator}

def store(request, category_slug = None):
    products = None
    category = None
    page_number= None
    page_products = None
    products_count = 0
    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=category).order_by('id')
        pages = listing(request, products)  
        page_number = pages['page_number']
        page_products = pages['page_products']
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        #paginator
        pages = listing(request, products)  
        page_number = pages['page_number']
        page_products = pages['page_products']
    products_count = products.count()

    context = {
        'products': page_products,
        'products_quantity' : products_count,
        'add_cart': add_cart,
        'page_number':page_number,
        'pages_range':pages['paginator'].page_range
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug , product_slug, is_active=False):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        cart = Cart.objects.get(cart_id = _cart_id(request))
        is_active = CartItem.objects.filter(cart=cart, product=single_product).exists()
    except Exception as e:
        pass
    context = {
        'single_product': single_product,
        'is_active': is_active
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    keyword = request.GET.get('keyword')
    products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains = keyword ))
    pages = listing(request, products)  
    page_number = pages['page_number']
    page_products = pages['page_products']
    context = {
        'products': page_products,
        'products_quantity': products.count(),
        'page_number':page_number,
        'pages_range':pages['paginator'].page_range
    }
    return render(request, 'store/store.html', context)