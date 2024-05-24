from django.shortcuts import render
from cart.cart import Cart
from payment.forms import ShippingForm


def payment_success(request):
    return render(request, "payment/payment_success.html", {})


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    if request.user.is_authenticated:
     
        # User chekcout
        
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)		
         
        render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities": quantities, "totals":totals}) 
     
     
     
    else:
     
        # Guest chekcout
        
        
        shipping_form = ShippingForm(request.POST or None)		
        
        return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities": quantities, "totals":totals}) 
    
