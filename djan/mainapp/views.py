from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# INDEX -> STRONA GŁOWNA

def index_view(request):
    # context -> proby
    user_data = {
        "name": budownictwo_view,
        "vip": False
    }

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        return HttpResponse(f"E-mail: {email} Pass: {password}")
    
    return render(request, 'index.html', user_data)

# LOGOWANIE I REJESTRACJA

def logowanie_view(request):
    return render(request, 'logowanie.html')

def rejestracja_view(request):
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