from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def index_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        return HttpResponse(f"E-mail: {email} Pass: {password}")
    return render(request, 'index.html')

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