from .models import Cart

def cart_item_count(request):
    # Initialize count to 0
    count = 0

    # Check if the user is logged in
    if request.user.is_authenticated:
        # Try to get the user's cart
        cart = Cart.objects.filter(customer=request.user).first()
        if cart:
            # If the cart exists, get the count of items in it
            count = cart.items.count()

    # Return a dictionary with the count. This will be available in all templates.
    return {'cart_item_count': count}