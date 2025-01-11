"""
URL configuration for djan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mainapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'),
    path('rejestracja/', rejestracja_view, name='rejestracja'),
    path('logowanie/', logowanie_view, name='logowanie'),
    path('logout/', logout_view, name='logout'),

    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'), 
    
    path('<slug:category_slug>', category_view, name='category'),
    
    path('order/', order, name='order'),
    
    path('koszyk/', koszyk_view, name='koszyk'),
    path('user_site/', user_site_view, name='user_site'),


    path('<slug:category_slug>/<slug:product_slug>/', product_detail_view, name='product_detail'),

    path('cart/<int:cart_id>/clear', clear_cart, name='clear_cart'),
    
    path('cart/<int:cart_product_id>/minus/', quantity_minus, name='quantity_minus'),
    path('cart/<int:cart_product_id>/plus/', quantity_plus, name='quantity_plus'),
    path('cart/<int:cart_product_id>/clear_product/', clear_product, name='clear_product'),
]
