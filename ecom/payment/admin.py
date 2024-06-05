from django.contrib import admin
from .models import ShippingAddress,Order, OrderItem
from django.contrib.auth.models import User

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

class OrderItemInline(admin.StackedInline):              # Create an OrderItem Inline
    model = OrderItem
    
    
class OrderAdmin(admin.ModelAdmin):                      #Extend our Order Model
    model = Order
    inlines = [OrderItemInline]
    
    
    
admin.site.unregister(Order)                                            #Unregister Order Model
admin.site.register(Order, OrderAdmin)                                 # Re-Register Order and OrderAdmin