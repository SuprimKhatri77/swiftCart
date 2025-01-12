from django.urls import path
from . import views


urlpatterns = [
    path('', views.shop, name='home'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('update-cart/', views.update_cart, name='update-cart'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]