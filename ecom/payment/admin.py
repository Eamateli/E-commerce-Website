from django.contrib import admin
from .models import ShippingAddress,Order, OrderItem
from django.contrib.auth.models import User

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

class OrderItemInline(admin.StackedInline):              # Create an OrderItem Inline
    model = OrderItem
    extra = 0
    
    
class OrderAdmin(admin.ModelAdmin):                      #Extend our Order Model
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user", "full_name", "email", "shipping_address", "amount_paid", "date_ordered", "shipped","date_shipped", "invoice","paid"]
    inlines = [OrderItemInline]
    
    
    
admin.site.unregister(Order)                                            #Unregister Order Model
admin.site.register(Order, OrderAdmin)                                 # Re-Register Order and OrderAdmin