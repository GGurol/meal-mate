from django.db import models
from django.contrib.auth.models import User

def get_menu_item_image_path(instance, filename):
    # upload path: media/restaurant_{id}/menu_items/{filename}
    return f'restaurant_{instance.restaurant.id}/menu_items/{filename}'

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    # CORRECTED: Made the ImageField optional instead of using an invalid default
    picture = models.ImageField(upload_to='restaurants/', null=True, blank=True)
    cuisine = models.CharField(max_length=200)
    rating = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.cuisine})"
    
class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=50)
    # CORRECTED: Made the ImageField optional
    picture = models.ImageField(upload_to=get_menu_item_image_path, null=True, blank=True)
    description = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_veg = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.price}"
    
class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    
    # CLEANED UP: Removed the unnecessary commented-out line

    def total_price(self):
        return sum(item.get_total() for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.customer.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total(self):
        return self.menu_item.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"
    
class Order(models.Model):
    STATUS_CHOICES = (
        ('Confirmed', 'Confirmed'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} for Order #{self.order.id}"