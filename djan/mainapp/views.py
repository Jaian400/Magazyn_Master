from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import WarehouseProduct
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager
from django.contrib.auth import authenticate, login
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

# INDEX -> STRONA GŁOWNA

def index_view(request):

    return render(request, 'index.html')

# LOGOWANIE I REJESTRACJA

def logowanie_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = email.split('@')[0]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if "magazynmaster.pl" in email.split('@')[1]:
                login(request, user)
                return redirect(reverse('admin:index')) 
            login(request, user)
            return render(request, 'index.html')
        else:
            return render(request, 'logowanie.html', {"error": "Niepoprawny e-mail lub hasło."})
    return render(request, 'logowanie.html')

def rejestracja_view(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            repeat_password = request.POST.get("repeat_password")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            user = None
        
            if len(password) <= 8:
                return render(
                    request, 
                    'rejestracja.html', 
                    {
                        "error": "Hasło musi mieć ponad 8 znaków.",
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name
                    }
                )

            elif not any(char.isdigit() for char in password):
                return render(
                    request,
                    'rejestracja.html',
                    {
                        "error": "Hasło musi zawierać cyfrę.",
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name
                    }
                    )
            
            elif not any(char.isupper() for char in password):
                return render(
                    request,
                    'rejestracja.html',
                    {
                        "error": "Hasło musi zawierać wielką literę.",
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name
                    }
                    )

            else:
                if (password==repeat_password):
                    user = User.objects.create_user(
                        username=email.split('@')[0],  # nazwa uzytkownika generowana z maila
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )
                else:
                    return render(
                        request,
                        'rejestracja.html',
                        {
                            "error": "Hasła nie są takie same.",
                            "email": email,
                            "first_name": first_name,
                            "last_name": last_name
                        }
                    )
            if user is not None:
                login(request, user)
                return render(request, 'index.html')
    except :
        return render(
            request, 'rejestracja.html',
                {
                    "error_email_taken": "Użytkownik o takim adresie email już istnieje.",
                    "first_name": first_name,
                    "last_name": last_name 
                }
        )
    return render(request, 'rejestracja.html')

# KOSZYK

def koszyk_view(request):
    return render(request, 'koszyk.html')

# PODSTRONY PRODUKTOW

def budownictwo_view(request):
    return render(request, 'budownictwo.html')

def kuchnia_view(request):
    return render(request, 'kuchnia.html')

def lazienka_view(request):
    return render(request, 'lazienka.html')

def mieszkanie_view(request):
    return render(request, 'mieszkanie.html')

def ogrod_view(request):
    return render(request,'ogrod.html')

def technika_view(request):
    return render(request, 'technika.html')