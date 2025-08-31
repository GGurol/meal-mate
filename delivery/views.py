from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from .models import Customer, Restaurant, MenuItem, Cart, Order, OrderItem, CartItem

# A simple check to see if the user is an admin/superuser
def is_admin(user):
    return user.is_superuser

# Home Page
def index(request):
    if request.user.is_authenticated:
        return redirect('customer_home')
    return render(request, 'delivery/index.html')

# Sign In Page
def signin(request):
    if request.user.is_authenticated:
        return redirect('customer_home')
    return render(request, 'delivery/signin.html')

# Sign Up Page
def signup(request):
    if request.user.is_authenticated:
        return redirect('customer_home')
    return render(request, 'delivery/signup.html')

def handle_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                # Redirect admins to the admin panel
                return redirect('/admin/')
            else:
                # Redirect regular users to the customer homepage
                return redirect('customer_home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'delivery/fail.html')

    return HttpResponse("Invalid request")


# Handle Sign Up (SECURE VERSION)
def handle_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            Customer.objects.create(user=user, mobile=mobile, address=address)
            
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('signin') # Assumes you have a URL with name='signin'
        except IntegrityError:
            messages.error(request, 'That username is already taken.')
            return redirect('signup') # Assumes you have a URL with name='signup'

    return HttpResponse("Invalid request")

# Decorator to ensure only admins can access these views
@user_passes_test(is_admin)
def add_restaurant_page(request):
    return render(request, 'delivery/add_restaurant.html')

@user_passes_test(is_admin)
def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

        Restaurant.objects.create(name=name, picture=picture, cuisine=cuisine, rating=rating)
        return redirect('show_restaurant_page') # Redirect to the restaurant list

    return HttpResponse("Invalid request")

@user_passes_test(is_admin)
def show_restaurant_page(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html', {"restaurants": restaurants})

@user_passes_test(is_admin)
def restaurant_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        is_veg = request.POST.get('is_veg') == 'on'
        picture = request.POST.get('picture')

        MenuItem.objects.create(
            restaurant=restaurant, name=name, description=description,
            price=price, is_veg=is_veg, picture=picture
        )
        return redirect('restaurant_menu', restaurant_id=restaurant.id)

    menu_items = restaurant.menu_items.all()
    return render(request, 'delivery/menu.html', {'restaurant': restaurant, 'menu_items': menu_items})

@user_passes_test(is_admin)
def update_restaurant_page(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'delivery/update_restaurant_page.html', {"restaurant": restaurant})

@user_passes_test(is_admin)
def update_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        restaurant.name = request.POST.get('name')
        restaurant.picture = request.POST.get('picture')
        restaurant.cuisine = request.POST.get('cuisine')
        restaurant.rating = request.POST.get('rating')
        restaurant.save()
        return redirect('show_restaurant_page')

@user_passes_test(is_admin)
def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    restaurant.delete()
    return redirect('show_restaurant_page')

@user_passes_test(is_admin)
def update_menuItem_page(request, menuItem_id):
    menuItem = get_object_or_404(MenuItem, id=menuItem_id)
    return render(request, 'delivery/update_menuItem_page.html', {"item": menuItem})

@user_passes_test(is_admin)
def update_menuItem(request, menuItem_id):
    menuItem = get_object_or_404(MenuItem, id=menuItem_id)
    if request.method == 'POST':
        menuItem.name = request.POST.get('name')
        menuItem.description = request.POST.get('description')
        menuItem.price = request.POST.get('price')
        menuItem.is_veg = request.POST.get('is_veg') == 'on'
        menuItem.picture = request.POST.get('picture')
        menuItem.save()
        return redirect('restaurant_menu', restaurant_id=menuItem.restaurant.id)

@user_passes_test(is_admin)
def delete_menuItem(request, menuItem_id):
    menuItem = get_object_or_404(MenuItem, id=menuItem_id)
    restaurant_id = menuItem.restaurant.id
    menuItem.delete()
    return redirect('restaurant_menu', restaurant_id=restaurant_id)

# Customer-facing views now use @login_required
@login_required
def customer_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = restaurant.menu_items.all()
    return render(request, 'delivery/customer_menu.html', {'restaurant': restaurant, 'menu_items': menu_items})

@login_required
def add_to_cart(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    # get count from form, default 1
    quantity = int(request.POST.get('quantity', 1))

    cart, created = Cart.objects.get_or_create(customer=request.user)
    
    # check if its in cart already
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item,
        # Eğer yeni oluşturulmuyorsa, varsayılanları uygula
        defaults={'quantity': quantity}
    )

    # increase the count if item already exists in cart
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f"Updated {menu_item.name} quantity in your cart!")
    else:
        messages.success(request, f"{menu_item.name} added to your cart!")

    return redirect('customer_menu', restaurant_id=menu_item.restaurant.id)


def show_cart_page(request):
    cart = Cart.objects.filter(customer=request.user).first()
    items = []
    total_price = 0
    
    # ADD THIS: A variable to hold the last restaurant's ID
    last_restaurant_id = None

    if cart:
        # Get cart items and total price
        items = cart.items.all()
        total_price = cart.total_price()
        
        # ADD THIS: If there are items, get the restaurant ID from the last one
        last_item = items.last()
        if last_item:
            last_restaurant_id = last_item.menu_item.restaurant.id

    context = {
        'items': items,
        'total_price': total_price,
        'last_restaurant_id': last_restaurant_id, # Pass the ID to the template
    }
    return render(request, 'delivery/cart.html', context)


@login_required
def checkout(request):
    cart = Cart.objects.filter(customer=request.user).first()
    if not cart or not cart.items.all().exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('show_cart_page') # Assumes you have a URL named 'show_cart_page'

    total_price = cart.total_price()
    
    order = Order.objects.create(
        customer=request.user, 
        total_price=total_price, 
        status='Confirmed'
    )
    
    # This loop is now corrected
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            menu_item=cart_item.menu_item,    # Get the MenuItem from the CartItem
            quantity=cart_item.quantity,       # Get the quantity from the CartItem
            price=cart_item.menu_item.price  # Get the price from the MenuItem
        )

    cart.delete()
    
    messages.success(request, f"Thank you! Your order #{order.id} has been confirmed.")

    restaurants = Restaurant.objects.all()
    return render(request, 'delivery/customer_home.html', {"restaurants": restaurants})

@login_required
def orders(request):
    # This view should probably show a list of past orders for the logged-in user
    past_orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'delivery/orders.html', {'orders': past_orders})

@login_required
def customer_home(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'delivery/customer_home.html', {"restaurants": restaurants})


@login_required
def order_history(request):
    """
    Fetches and displays all past orders for the logged-in user.
    """
    past_orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'orders': past_orders
    }
    return render(request, 'delivery/order_history.html', context)