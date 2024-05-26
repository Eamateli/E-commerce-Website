from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm
from .models import ShippingAddress
from django.contrib import messages


def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants    
        totals = cart.cart_total()
        #Is user logged in 
        if request.user.is_authenticated:
            return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST})

        else:
            pass
        
        
        
        shipping_form = request.POST
        return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})
    else:
        messages.success(request, "Access Denied")
        return redirect ('home')
    


def payment_success(request):
    return render(request, "payment/payment_success.html", {})


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    if request.user.is_authenticated:
		# Checkout as logged in user
		# Shipping User
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		# Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form })
    else:
		# Checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})

    
