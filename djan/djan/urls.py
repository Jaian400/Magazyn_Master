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
from mainapp.views import (
    index_view, budownictwo_view,
    kuchnia_view, lazienka_view, mieszkanie_view, ogrod_view, technika_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'),
    path('budownictwo/', budownictwo_view, name='budownictwo'),
    path('kuchnia/', kuchnia_view, name='kuchnia'),
    path('lazienka/', lazienka_view, name='lazienka'),
    path('mieszkanie/', mieszkanie_view, name='mieszkanie'),
    path('ogrod/', ogrod_view, name='ogrod'),
    path('technika/', technika_view, name='technika'),
]
