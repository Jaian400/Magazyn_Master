from django.shortcuts import render
from django.http import HttpResponse

def index_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        return HttpResponse(f"Imię: {name}, E-mail: {email}")
    return render(request, "index.html")
