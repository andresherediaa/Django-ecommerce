from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from .forms import RegistrationForm
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

def account_activated(func):
    def wrapper_login(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper_login


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
                ##Send email confirmation
                subject = 'Confirma tu Cuenta!'
                message = render_to_string('accounts/email_confirmation.html',{
                    'user': user,
                    'domain' : get_current_site(request),
                    'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user)
                })
                email = EmailMessage(
                    subject,
                    message,
                    'andres.heredia@uazuay.edu.ec', 
                    [email],
                )
                email.content_subtype = "html"
                email.send()
                ########
            
                messages.success(request, '¡Registro exitoso! Te hemos enviado un email para que verifiques tu cuenta.')
                
                return redirect('login')
            except Exception as e :
                pass
            return redirect('register')
    else:
        form= RegistrationForm()
    return render(request, 'accounts/register.html', {'form':form})

@account_activated
def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        # user Authentication
        user = authenticate(email=email, password=password)
        is_activate = Account.objects.get(email=email).is_active 
        print("user==>", user)
        if is_activate == False:
            return render(request, 'accounts/login.html', {'is_activate': is_activate, 'email': email})
        if user is not None:
            login(request, user)
            messages.success(request, '¡Inicio de sesión exitoso!')
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
    print("request.COOKIES['sessionid']", request.COOKIES['sessionid'])
    print("request.USER", request.user, request.user.is_authenticated)
    
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
        
     
  
    