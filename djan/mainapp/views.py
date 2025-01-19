from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import admin
from django.urls import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from decimal import Decimal
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
# from django.contrib.auth.views import (
#     PasswordResetView, 
#     PasswordResetDoneView, 
#     PasswordResetConfirmView,
#     PasswordResetCompleteView
# )

# INDEX -> STRONA GŁOWNA

def index_view(request):

    # if request.method == 'POST':

    #     search_query = request.POST.get('query')

    #     return redirect(reverse('category', args=['all_products']) + f'?query={search_query}')
    
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
    request.session.delete()

    logout(request)
    return redirect(reverse('index')) 

# def PasswordResetView:



# PRODUKT

def product_detail_view(request,category_slug, product_slug): 
    category = get_object_or_404(ProductCategory, slug=category_slug)
    product = get_object_or_404(WarehouseProduct, slug=product_slug)
    
    return render(request, 'product_detail.html', {'product': product, 'category': category})

# ------------------------------------------------------------------------------------------------------------
# KOSZYK
# ------------------------------------------------------------------------------------------------------------

def koszyk_view(request):
    Cart.delete_old_carts()

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)

    cart_products = CartProduct.objects.filter(cart=cart)
    total_price = cart.total_price
    
    return render(request, 'koszyk.html', {'cart': cart, 'cart_products': cart_products, 'total_price': total_price})

# Dodwanie do koszyka
def add_to_cart(request, product_id):
    Cart.delete_old_carts()

    if request.method == 'POST':
        quantity = request.POST.get('quantity')

    product = get_object_or_404(WarehouseProduct, id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    
    if product.product_discount > 0:
        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product, product_price=product.product_price_discounted)
    else:
        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product, product_price=product.product_price)

    if not created:
        cart_product.product_quantity += int(quantity)
    else:
        cart_product.product_quantity += int(quantity) - 1

    cart_product.save()

    return redirect('koszyk')

# Czyszczenie koszyka
def clear_cart(request, cart_id):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    
    cart.clear_cart()
    return redirect('koszyk')

# obsluga koszyka -> produktow pojedynczych
def quantity_minus(request, cart_product_id):
    cart_product = CartProduct.objects.get(id=cart_product_id)
    cart_product.quantity_minus()
    return redirect('koszyk')

def quantity_plus(request, cart_product_id):
    cart_product = CartProduct.objects.get(id=cart_product_id)
    cart_product.quantity_plus()
    return redirect('koszyk')

def clear_product(request, cart_product_id):
    cart_product = CartProduct.objects.get(id=cart_product_id)
    cart_product.clear_product()
    return redirect('koszyk')

# ------------------------------------------------------------------------------------------------------------
# ZAMOWIENIE
# ------------------------------------------------------------------------------------------------------------

def order_view(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        try:
            last_order = Order.objects.filter(user=request.user).latest('created_at')
        except Order.DoesNotExist:
            last_order = None
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    
    if not cart.cartproduct_set.exists():
        return render(request, 'koszyk.html', {'error': 'Koszyk jest pusty.'})

    cart_products = CartProduct.objects.filter(cart=cart)
    total_price = cart.total_price + Decimal(9.0)

    if last_order == None:
        return render(request, 'order.html', {'cart': cart, 'cart_products': cart_products, 'total_price': total_price})
    else:
        return render(request, 'order.html', {'cart': cart, 'cart_products': cart_products, 'total_price': total_price, 'last_order' : last_order})

def send_confirmation_mail(order):
    try:
        subject=f"Potwierdzenie zamówienia nr {order.order_id}"
        message = render_to_string(
            "confirmation_order_mail.html",
            context={"order": order},
        )
        send_mail(subject, '', settings.EMAIL_HOST_USER, [order.email], html_message=message,)
    except Exception as e:
        print(f'Error sending email: {e}')

def order_complete_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        business_name = request.POST.get("company")
        nip = request.POST.get("NIP")
        area_code = request.POST.get("area_code")
        phone_number = request.POST.get("phone_number")
        country = request.POST.get("country")
        address_street = request.POST.get("street")
        address_building_number = request.POST.get("building_number")
        address_apartment_number = request.POST.get("apartment_number")
        zip_code = request.POST.get("zip_code")
        city = request.POST.get("city")
        
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        order = Order.objects.create(user=request.user, total_price=0.)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        order = Order.objects.create(total_price=0.)

    order.first_name=first_name
    order.last_name=last_name
    order.email=email
    order.business_name=business_name
    order.nip=nip
    order.area_code=area_code
    order.phone_number=phone_number
    order.country=country
    order.address_street=address_street
    order.address_building_number=address_building_number
    order.zip_code=zip_code
    order.city=city

    if address_apartment_number is not '':
        order.address_apartment_number=address_apartment_number 

    order.make_order(cart)
    # for cart_product in cart.items.all():
    #     Order.objects.create(order=order, order_product=cart_product.product, order_product_price=cart_product.product_price,
    #                          order_product_quantity=cart_product.product_quantity)
    # order.calculate_total_price()

    cart.clear_cart()
    
    send_confirmation_mail(order)
    return render(request, 'order_complete.html', {'order': order})

# ------------------------------------------------------------------------------------------------------------
# PODSTRONY PRODUKTOW
# ------------------------------------------------------------------------------------------------------------

def category_view(request, category_slug):
    category = get_object_or_404(ProductCategory, slug=category_slug)

    if category.category_name == 'All_products':
        products = WarehouseProduct.objects.all()
    else:
        products = WarehouseProduct.objects.filter(product_category=category)
    
    max_price = int(max(product.product_price for product in products) + 1)
    suppliers = products.values_list('product_market__supplier__supplier_name', flat=True).distinct()

    supplier_filter = request.GET.getlist('supplier')
    if supplier_filter:
        products = products.filter(product_market__supplier__supplier_name__in=supplier_filter)

    products = filter_products(products, request)

    # Wyszukiwanie 
    if request.method == 'POST':
        search_query = request.POST.get('query')
        products = products.filter(product_name__icontains=search_query)

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
# WYSZUKIWANIE
# ------------------------------------------------------------------------------------------------------------

def search_view(request):
    products = WarehouseProduct.objects.all()

    if request.method == 'POST':
        search_query = request.POST.get('query')
        initial_matches = products.filter(product_name__icontains=search_query)
        initial_ids = list(initial_matches.values_list('id', flat=True))

        all_product_names = list(products.values_list('id', 'product_name'))

        fuzzy_matches = process.extract(search_query, [name for _, name in all_product_names], scorer=fuzz.partial_ratio, limit=50)
        matched_ids = [
            product_id
            for product_id, product_name in all_product_names
            if any(product_name == match[0] and match[1] > 70 for match in fuzzy_matches)
        ]

        all_matched_ids = set(initial_ids + matched_ids)

        products = products.filter(id__in=all_matched_ids)

    # proste wyszukiwanie
    # if request.method == 'POST':
    #     search_query = request.POST.get('query')
    #     products = products.filter(product_name__icontains=search_query)

    return render(request, 'search.html', {'products': products})

# ------------------------------------------------------------------------------------------------------------
# STRONA KONTA UŻYTKOWNIKA
# ------------------------------------------------------------------------------------------------------------

@csrf_protect
def user_site_view(request):

    if not request.user.is_authenticated:
        return redirect('logowanie')

    orders = Order.objects.filter(user=request.user)

    return render(request, 'user_site.html', {'orders': orders} )

