from .cart import Cart

# Create contect rpcessor so our cart can work on all pages 

def cart(request):
    return {'cart': Cart(request)}