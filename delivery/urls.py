from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # <-- Add this import
 
urlpatterns = [
    # Home and authentication paths
    #path('', views.index, name='index'),
    path('', views.index, name='home'), # name='home' has been added
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.handle_login, name='handle_login'),
    path('signup/submit/', views.handle_signup, name='handle_signup'),
    path('home/', views.customer_home, name='customer_home'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Restaurant-related paths (for Admins)
    path('restaurants/add-page/', views.add_restaurant_page, name='add_restaurant_page'),
    path('restaurants/', views.show_restaurant_page, name='show_restaurant_page'),
    path('restaurants/add/', views.add_restaurant, name='add_restaurant'),
    path('restaurants/<int:restaurant_id>/menu/', views.restaurant_menu, name='restaurant_menu'),
    path('restaurants/<int:restaurant_id>/update/', views.update_restaurant, name='update_restaurant'),
    path('restaurants/<int:restaurant_id>/update-page/', views.update_restaurant_page, name='update_restaurant_page'),
    path('restaurants/<int:restaurant_id>/delete/', views.delete_restaurant, name='delete_restaurant'),

    # MenuItem-related paths (for Admins)
    path('menuitem/<int:menuItem_id>/update/', views.update_menuItem, name='update_menuItem'),
    path('menuitem/<int:menuItem_id>/update-page/', views.update_menuItem_page, name='update_menuItem_page'),
    path('menuitem/<int:menuItem_id>/delete/', views.delete_menuItem, name='delete_menuItem'),

    # --- UPDATED CUSTOMER-FACING PATHS (username removed) ---
    path('restaurants/<int:restaurant_id>/customer-menu/', views.customer_menu, name='customer_menu'),
    path('cart/', views.show_cart_page, name='show_cart_page'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('order-history', views.order_history, name='order_history'),
]