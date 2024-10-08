from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime
#Paypal
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid #unique user id for duplicate orders


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)     #Get order
        items = OrderItem.objects.filter(order=pk)   #Get the order items
        
        if request.POST:
            status = request.POST['shipping_status']
            if status == "true":     #Check if true or false
                order = Order.objects.filter(id=pk)   #Get the order
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)   #Update the status
            else:
                order = Order.objects.filter(id=pk)   
                order.update(shipped=False)   
            messages.success(request, "Shipping status updated.")
            return redirect('home')
                
                
                
        return render(request, 'payment/orders.html', {"order":order, "items":items})
      
    
    
    else:
        messages.success(request, "Access Denied")
        return redirect ('home')
        


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)  #Get the order
            now = datetime.datetime.now() #Grab date
            order.update(shipped=True, date_shipped=now)   #Update the order status
            messages.success(request, "Shipping status updated.") #Redirect 
            return redirect('not_shipped_dash')
        return render(request, "payment/not_shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect ('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)  #Grab order
            now = datetime.datetime.now() #Grab date
            order.update(shipped=False)   #Update the order status
            messages.success(request, "Shipping status updated.") #Redirect 
            return redirect('shipped_dash')
        return render(request, "payment/shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect ('home')


def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants    
        totals = cart.cart_total()
        #Get billing info
        payment_form = PaymentForm(request.POST or None)
        #Get shipping session data
        my_shipping = request.session.get('my_shipping')
        #Gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        
        
        #Create shipping address from session info 
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals
        
        #Create order
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            
            
            #Add order items
            order_id = create_order.pk #Get order info
            for product in cart_products():
                product_id = product.id  #Get product id
                if product.is_sale:  #Get product price
                    price = product.sale_price
                else:
                    price = product.price
                    
            for key,value in quantities().items(): #Get quantity 
                if int(key) == product.id:
                    create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                    create_order_item.save()
                    
        for key in list(request.session.keys()):               #Delete cart       
            if key == "session_key " :
                del request.session[key]
                
        current_user = Profile.objects.filter(user__id=request.user.id)   #Delete cart from DB (old_car field)
        current_user.update(old_cart="")  #Delete shopping cart in DB (old_cart field)
            
        messages.success(request, "Order Placed!")
        return redirect ('home')
            
    else:
        create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
        create_order.save()
            
            
            #Add order items
        order_id = create_order.pk #Get order info
        for product in cart_products():
             product_id = product.id  #Get product id
             if product.is_sale:  #Get product price
                price = product.sale_price
             else:
                price = product.price
                    
    for key,value in quantities().items(): #Get quantity 
        if int(key) == product.id:
            create_order_item = OrderItem(order_id=order_id, product_id=product_id,quantity=value, price=price)
            create_order_item.save()
                    
        for key in list(request.session.keys()):               #Delete cart       
            if key == "session_key " :
                del request.session[key]
            
            messages.success(request, "Order Placed!")
            return redirect ('home')
        
        
    else:
        messages.success(request, "Access Denied")
        return redirect ('home')
        


def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants    
        totals = cart.cart_total()
        #Creat a session with Shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        #Create shipping address from session info 
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals
        #Get the host
        host = request.get_host()
        #Create Invoice Number
        my_Invoice = str(uuid.uuid4())
        #Paypal form and Dictionary
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVERVER_EMAIL,
            'amount': totals,
            'item_name': 'Book Order',
            'no_shipping': '2',
            'invoice': my_Invoice,
            'currency_code':'USD',
            'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
            'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
            'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),  
            
        }
        #Paypal button
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)
        
        
        #Is user logged in 
        if request.user.is_authenticated:
            billing_form = PaymentForm()
            
            
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid, invoice=my_Invoice)
            create_order.save()
            
            
            #Add order items
            order_id = create_order.pk #Get order info
            for product in cart_products():
                product_id = product.id  #Get product id
                if product.is_sale:  #Get product price
                    price = product.sale_price
                else:
                    price = product.price
                    
            for key,value in quantities().items(): #Get quantity 
                if int(key) == product.id:
                    create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                    create_order_item.save()
                
        current_user = Profile.objects.filter(user__id=request.user.id)   #Delete cart from DB (old_car field)
        current_user.update(old_cart="")  #Delete shopping cart in DB (old_cart field)
            
        return render(request, "payment/billing_info.html", {"paypal_form":paypal_form,"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST,"billing_form":billing_form})

            
    else:
        create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid, invoice=my_Invoice)
        create_order.save()
            
            
            #Add order items
        order_id = create_order.pk #Get order info
        for product in cart_products():
             product_id = product.id  #Get product id
             if product.is_sale:  #Get product price
                price = product.sale_price
             else:
                price = product.price
                    
    for key,value in quantities().items(): #Get quantity 
        if int(key) == product.id:
            create_order_item = OrderItem(order_id=order_id, product_id=product_id,quantity=value, price=price)
            create_order_item.save()
             
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"paypal_form":paypal_form,"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})
       
        
    else:
        messages.success(request, "Access Denied")
        return redirect ('home')
    


def payment_success(request):
    return render(request, "payment/payment_success.html", {})

def payment_failed(request):
    return render(request, "payment/payment_failed.html", {})


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

    
