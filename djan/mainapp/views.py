from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import WarehouseProduct
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager

# INDEX -> STRONA GŁOWNA

def index_view(request):

    return render(request, 'index.html')

# LOGOWANIE I REJESTRACJA

def logowanie_view(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        #return HttpResponse(f"E-mail: {email} Pass: {password}")
    return render(request, 'logowanie.html')

def rejestracja_view(request):
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        repeat_password = request.POST.get("repeat_password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        if (password==repeat_password):
            user = User.objects.create_user(
                username=email.split('@')[0],  # Default username from email
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        else:
            return render(request, 'rejestracja.html', {"error": "Hasła nie są takie same."})
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