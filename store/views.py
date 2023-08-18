from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category

def store(request, category_slug = None):
    products = None
    category = None
    products_count=0
    if category_slug != None:
        ##category = Category.objects.filter(slug=category_slug).first()
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=category)
    else:
        products = Product.objects.all().filter(is_available=True)
    products_count = products.count()
    context = {
        'products': products,
        'products_quantity' : products_count
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug , product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    context = {
        'single_product':single_product
    }
    return render(request, 'store/product_detail.html', context)