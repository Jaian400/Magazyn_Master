from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import WarehouseProduct, ProductCategory, Cart, CartProduct
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import admin
from django.urls import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
import uuid

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
            return redirect(reverse('index')) 
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

            # kreacja koszyka dla usera
            Cart.objects.create(user=user)

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

def logout_view(request):

    logout(request)
    return redirect(reverse('index')) 

# PRODUKT

def product_detail_view(request,category_slug, product_slug): 
    category = get_object_or_404(ProductCategory, slug=category_slug)
    product = get_object_or_404(WarehouseProduct, slug=product_slug)
    
    return render(request, 'product_detail.html', {'product': product, 'category': category})

# ------------------------------------------------------------------------------------------------------------
# KOSZYK
# ------------------------------------------------------------------------------------------------------------

def koszyk_view(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_uuid = uuid.uuid4()
        cart, created = Cart.objects.get_or_create(session_uuid=cart_uuid)

    cart_products = CartProduct.objects.filter(cart=cart)
    total_price = cart.total_price
    
    # cart_products -> wyswietl w petli, one maja ilosc swoja, jesli chcesz manipulacje nia,
    # to zglos sie do @Jaian400 i to trzeba bedzie zobaczyc, obsluzyc
    # total_price -> po prostu wyswietl cene calkowita koszyka
    return render(request, 'koszyk.html', {'cart_products': cart_products, 'total_price': total_price})

# Dodwanie do koszxyka
def add_to_cart(request, product_id):
    product = get_object_or_404(WarehouseProduct, id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_uuid = uuid.uuid4()
        cart, created = Cart.objects.get_or_create(session_uuid=cart_uuid)
    
    if product.product_discount > 0:
        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product, product_price=product.product_price_discounted)
    else:
        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product, product_price=product.product_price)

    if not created:
        cart_product.product_quantity += 1

    cart_product.save()

    return redirect('koszyk')

# Czyszczenie koszyka
def clear_cart(request, cart_id):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
    else:
        cart = Cart.objects.get(session=request.session.session_key)
    
    cart.clear_cart()
    return redirect('koszyk')

# obsluga koszyka -> produktow pojedynczych
def quantity_minus(request, cart_product_id):
    cart_product = CartProduct.objects.get(id=cart_product_id)
    cart_product.quantity_minus()
    return redirect('cart')

def quantity_plus(request, cart_product_id):
    cart_product = CartProduct.objects.get(id=cart_product_id)
    cart_product.quantity_plus()
    return redirect('cart')

def clear_product(request, cart_product_id):
    cart_product = CartProduct.objects.get(id=cart_product_id)
    cart_product.clear_product()
    return redirect('cart')

# Widok do składania zamówienia (na razie opróżnia koszyk)
def order(request):
    request.session['cart'] = {}
    return redirect('koszyk')

# ------------------------------------------------------------------------------------------------------------
# PODSTRONY PRODUKTOW - trzeba dynamicznie zrobic
# ------------------------------------------------------------------------------------------------------------

def category_view(request, category_slug):
    category = get_object_or_404(ProductCategory, slug=category_slug)
    products = WarehouseProduct.objects.filter(product_category=category)
    max_price = int(max(product.product_price for product in products) + 1)
    suppliers = products.values_list('product_market__supplier__supplier_name', flat=True).distinct()

    # Filter by suppliers
    supplier_filter = request.GET.getlist('supplier')
    if supplier_filter:
        products = products.filter(product_market__supplier__supplier_name__in=supplier_filter)

    products = filter_products(products, request)

    return render(request, 'category.html', {'products': products, 'category': category, 'max_price': max_price, 'suppliers': suppliers})

# ------------------------------------------------------------------------------------------------------------
# FILTROWANIE
# ------------------------------------------------------------------------------------------------------------

def filter_products(queryset, request):
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    # categories = request.GET.getlist('category')
    # suppliers = request.GET.getlist('supplier')

    if min_price:
        queryset = queryset.filter(product_price__gte=min_price)
    if max_price:
        discounted_products = queryset.filter(product_discount__gt=0, product_price_discounted__lte=max_price)
        regular_products = queryset.filter(product_discount=0, product_price__lte=max_price)
        queryset = discounted_products | regular_products

    # if categories:
    #     queryset = queryset.filter(product_category__id__in=categories)

    # if suppliers:
    #     queryset = queryset.filter(product_market__supplier__supplier_id__in=suppliers)

    return queryset

# ------------------------------------------------------------------------------------------------------------
# strona konta uzytkownika
# ------------------------------------------------------------------------------------------------------------

@csrf_protect
def user_site_view(request):

    if not request.user.is_authenticated:
        return redirect('logowanie')



    return render(request, 'user_site.html')
