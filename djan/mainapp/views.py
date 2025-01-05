from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import WarehouseProduct, ProductCategory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import admin
from django.urls import reverse
from django.db import IntegrityError

# INDEX -> STRONA GŁOWNA

def index_view(request):
    products = WarehouseProduct.objects.filter(product_category__category_name="index") #Trzeba przemyśleć jak chcemy wyświetlać rzeczy na głównej
    return render(request, 'index.html', {'products': products})

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
            error_length = None
            error_number = None
            error_capital_letter = None
            error_repeat = None
        
            if len(password) <= 8:
                error_length = "Hasło musi mieć ponad 8 znaków."

            if not any(char.isdigit() for char in password):
                error_number = "Hasło musi zawierać cyfrę."

            if not any(char.isupper() for char in password):
                error_capital_letter = "Hasło musi zawierać wielką literę."

            if not password==repeat_password:
                error_repeat = "Hasła nie są takie same."

            if not (error_length or error_number or error_capital_letter or error_repeat):
                user = User.objects.create_user(
                    username=email.split('@')[0],  # nazwa uzytkownika generowana z maila
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )

            if error_length or error_number or error_capital_letter or error_repeat:
                return render(
                request,
                'rejestracja.html',
                    {
                    "error_length": error_length,
                    "error_number": error_number,
                    "error_capital_letter": error_capital_letter,
                    "error_repeat": error_repeat,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name
                    }
                )
            if user is not None:
                login(request, user)
                return render(request, 'index.html')
    except IntegrityError:
        return render(
            request, 'rejestracja.html',
                {
                    "error_email_taken": "Użytkownik o takim adresie email już istnieje.",
                    "first_name": first_name,
                    "last_name": last_name 
                }
        )
    return render(request, 'rejestracja.html')

# PRODUKT

def product_detail_view(request,category_slug, product_slug): 
    category = get_object_or_404(ProductCategory, slug=category_slug)
    product = get_object_or_404(WarehouseProduct, slug=product_slug)
    
    return render(request, 'product_detail.html', {'product': product, 'category': category})

# KOSZYK

def koszyk_view(request):
    return render(request, 'koszyk.html')

# PODSTRONY PRODUKTOW - mozna dynamicznie zrobic

def budownictwo_view(request):
    products = WarehouseProduct.objects.filter(product_category__category_name="budownictwo")  # Pobranie wszystkich produktów
    return render(request, 'budownictwo.html', {'products': products})

def kuchnia_view(request):
    products = WarehouseProduct.objects.filter(product_category__category_name="kuchnia")
    return render(request, 'kuchnia.html', {'products': products})

def lazienka_view(request):
    products = WarehouseProduct.objects.filter(product_category__category_name="lazienka")
    return render(request, 'lazienka.html', {'products': products})

def mieszkanie_view(request):
    products = WarehouseProduct.objects.filter(product_category__category_name="mieszkaniea")
    return render(request, 'mieszkanie.html', {'products': products})

def ogrod_view(request):
    products = WarehouseProduct.objects.filter(product_category__category_name="ogrod")
    return render(request,'ogrod.html', {'products': products})

def technika_view(request):
    products = WarehouseProduct.objects.filter(product_category__category_name="technika")
    return render(request, 'technika.html', {'products': products})