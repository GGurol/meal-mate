from django.contrib import admin
# Make sure to import all the models you want to see in the admin
from .models import Customer, Restaurant, MenuItem, Cart, CartItem, Order, OrderItem

# This allows OrderItems to be edited directly within the Order admin page
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'quantity', 'price') 

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# This customizes the display for the Order model
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'total_price', 'status')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

# --- Register ALL your models here ---

admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(CartItem)
# We register Order with our custom OrderAdmin class
admin.site.register(Order, OrderAdmin)