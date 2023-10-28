from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from .forms import RegistrationForm, RestorePasswordForm
from .models import Account
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from accounts.models import Account
from carts.models import Cart, CartItem
from carts.views import _cart_id
from urllib.parse import urlparse, parse_qs

def account_activated(func):
    def wrapper_login(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper_login

def send_email(request,user, email, subject, template_url):
    ##Send email 
    subject = subject
    message = render_to_string(template_url,{
        'user': user,
        'domain' : get_current_site(request),
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : default_token_generator.make_token(user)
    })
    mail = EmailMessage(
        subject,
        message,
        'andres.heredia@uazuay.edu.ec', 
        [email],
    )
    mail.content_subtype = "html"
    mail.send()


def register(request):
    if request.method == 'POST':
        form= RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            username = email.split('@')[0]
            password = form.cleaned_data.get('password')
            phone_number = form.cleaned_data.get('phone_number')
            try: 
                user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
                user.phone_number=phone_number
                user.save()
                send_email(request, user, email, 'Confirma tu Cuenta!', 'accounts/email_confirmation.html')
                messages.success(request, '¡Registro exitoso! Te hemos enviado un email para que verifiques tu cuenta.')
                return redirect('login')
            except Exception as e :
                pass
            return redirect('register')
    else:
        form= RegistrationForm()
    return render(request, 'accounts/register.html', {'form':form})

def update_variation(request, cart_items_anonymus, user):
    variations_logged_in = []
    existing_variations = [] #cart item from anonymous session 
    cart_items_user= CartItem.objects.filter(user= user)   
    
    for cart_item in cart_items_user:
        product_variation = cart_item.variations.all()
        variations_logged_in.append(product_variation)
    
    for cart_item in cart_items_anonymus:
        product_variation = cart_item.variations.all()
        existing_variations.append(product_variation) #[<QuerySet [<Variation: red>, <Variation: large>]>, <QuerySet [<Variation: white>, <Variation: medium>]>]
    
    variations_logged_in_flat = [(list(qs.values_list('variation_value', flat=True)) + list(qs.values_list('product__product_name', flat=True))) for qs in variations_logged_in]
    # Crear una lista plana de variaciones a partir de los QuerySets en existing_variations
    existing_variations_flat = [(list(qs.values_list('variation_value', flat=True)) + list(qs.values_list('product__product_name', flat=True))) for qs in  existing_variations]

    # Convertir las listas de variaciones en conjuntos para facilitar la comparación
    variations_logged_in_set = [set(variations) for variations in variations_logged_in_flat]
    existing_variations_set = [set(variations) for variations in existing_variations_flat]
    # Encontrar las variaciones que existen en ambas lista
    common_variations_user = [(variation, index, existing_variations_set.index(variation)) for index, variation in enumerate(variations_logged_in_set) if variation in existing_variations_set]
    
    new_cart_items= [index for index, variation in enumerate(existing_variations_set) if variation not in variations_logged_in_set]
    #variations_logged_in_flat111 = [list(qs.values_list('is_active', flat=True)) for qs in variations_logged_in]
    
    for item in common_variations_user:
        cart_items_user[item[1]].quantity += cart_items_anonymus[item[2]].quantity
     
    for index in new_cart_items:
        elemento_anonymus = cart_items_anonymus[index]
        # Crea una lista que contenga el elemento de cart_items_anonymus
        elemento_anonymus_list = [elemento_anonymus]
        # Convierte cart_items_user en una lista
        cart_items_user_list = list(cart_items_user)
        # Combina cart_items_user_list con elemento_anonymus_list
        cart_items_user = cart_items_user_list + elemento_anonymus_list

    return cart_items_user

@account_activated
def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        # user Authentication
        user = authenticate(email=email, password=password)
        is_activate = Account.objects.get(email=email).is_active 
        if is_activate == False:
            return render(request, 'accounts/login.html', {'is_activate': is_activate, 'email': email})
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id= _cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exist:
                    cart_items = CartItem.objects.filter(cart=cart)
                    updated_cart_items = update_variation(request, cart_items, user)
                    for item in updated_cart_items:
                        item.user= user
                        item.save()   
            except:
                pass
            login(request, user)
            messages.success(request, '¡Inicio de sesión exitoso!')
            ##check if we muwt go to checkout page or dashborad
            if 'HTTP_REFERER' in request.META:
                try:
                    referer = request.META['HTTP_REFERER']
                    parsed_url = urlparse(referer)
                    query_params_dict = parse_qs(parsed_url.query)
                    return redirect(query_params_dict['next'][0])
                except Exception as e:
                    return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales incorrectas. Inténtalo de nuevo.')
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '¡Cierre de sesión exitoso!')
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def activate(request, uid, token):
    try:
        uid64= urlsafe_base64_decode(uid).decode()
        user = Account.objects.get(id=uid64)
        if default_token_generator.check_token(user, token):
            user.is_active= True
            user.save()
            messages.success(request, 'Tu cuenta fue activada con exito :)!.')
            return redirect('login')
        else:
            messages.error(request, 'El enlace de activación no es válido :(.')
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        messages.error(request, 'El enlace de activación no es válido.')
    return redirect('login')
        
def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        user = Account.objects.filter(email__exact=email).first()
        if user:
            send_email(request, user, email, 'Restore Password!', 'accounts/restore_password_email.html')
            return redirect('login')
        else:
            messages.error(request, 'Account was not found !, Please check and try again.')
    return render(request, 'accounts/forgot_password.html')

def restore(request, uid, token):
    if request.method == "POST":
        form= RestorePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            try:
                uid64= urlsafe_base64_decode(uid).decode()
                user = Account.objects.get(id=uid64)
                if default_token_generator.check_token(user, token):
                    user.set_password(password)
                    user.save()
                    messages.success(request, 'Contrasena actualizada con exito!.')
                    return redirect('login')
                else:
                    raise ValueError
            except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
                messages.error(request, 'The link is invalid or expired')
        else:
            messages.error(request, "Passwords do not match!")
    else:
        form= RestorePasswordForm()
    return render(request, 'accounts/restore_password_form.html', {'form': form})
  
    