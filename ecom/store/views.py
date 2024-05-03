from django.shortcuts import render
from .models import Product

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products':products})

def about(request):
    return render(request, 'about.html', {})


def login_user(request):
    return render(request, 'login.html', {})

def logout_user(request):
    pass
    