import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import OrderForm
from carts.models import CartItem
from .models import Order
from carts.views import getTotalQuanityTax
# Create your views here.

def place_order(request):
  current_user = request.user
  cart_items = CartItem.objects.filter(user=current_user, is_active=True)
  
  if cart_items.count() <= 0:
    return redirect('store')
  
  
  if request.method == 'POST':
    form = OrderForm(request.POST)
    if form.is_valid():
      #save billing addres to DB
      order = Order()
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      email = form.cleaned_data['email']
      phone = form.cleaned_data['phone']
      address_line_1 = form.cleaned_data['address_line_1']
      address_line_2 = form.cleaned_data['address_line_2']
      country = form.cleaned_data['country']
      state = form.cleaned_data['state']
      city = form.cleaned_data['city']
      order_note = form.cleaned_data['order_note']
      prices= getTotalQuanityTax(cart_items)
      
      #save DB
      #payment ='9999'
      order.user = current_user
      order.first_name = first_name
      order.last_name = last_name
      order.phone = phone
      order.email = email
      order.address_line_1 = address_line_1
      order.address_line_2 = address_line_2
      order.country = country
      order.state = state
      order.city = city
      order.order_note = order_note
      order.order_total= prices['total']
      order.tax=  prices['tax']
      order.ip = request.META.get('REMOTE_ADDR')
      order.save()

      yr = int(datetime.date.today().strftime('%Y'))
      dt = int(datetime.date.today().strftime('%d'))
      mt = int(datetime.date.today().strftime('%m'))
      d = datetime.date(yr, mt, dt)
      current_date = d.strftime('%Y%m%d')
      order_number = current_date + str(order.id)
      order.order_number = order_number
      order.save()
      current_order = Order.objects.get(user=current_user, is_ordered=False, order_number= order_number)
      context = {
        'cart_items' : cart_items,
        'order' : current_order,
        'total_without_tax': prices['subtotal_str'],
        'total_tax': prices['tax_str'],
        'total': prices['total_str']
      }
      return render(request, 'orders/payment.html', context)
  else:
    return redirect('checkout')
  
def payment(request):
  return render(request, 'orders/payment.html')
      
  