from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from urllib.parse import unquote
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Create your views here.
@login_required
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_name = unquote(data.get("name")).strip()  # Decode the name properly
            print('Decoded Product Name:', product_name)  # Debugging line

            # Ensure product name is provided
            if not product_name:
                return JsonResponse({"error": "Product name is required"}, status=400)

            # Get customer and their active order
            customer, _ = Customer.objects.get_or_create(user=request.user)
            order, _ = Order.objects.get_or_create(customer=customer, complete=False)

            # Log for debugging: Check if product exists in the database
            print(f"Looking for product with name: {product_name}")

            # Get the product using its name
            try:
                product = Product.objects.get(name__iexact=product_name)  # Case-insensitive search
                print(f"Product found: {product.name}")  # Debugging line if found
            except Product.DoesNotExist:
                print(f"Product not found: {product_name}")  # Debugging line if not found
                return JsonResponse({"error": "Product not found"}, status=404)

            # Get or create the OrderItem for the product
            order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
            order_item.quantity += 1
            order_item.save()

            # Return updated cart details
            return JsonResponse({
                "message": f"{product.name} added to cart",
                "cart_items_count": order.get_cart_items,
                "cart_total": order.get_cart_total
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)



def shop(request):
    products = Product.objects.all()
    cart_items_count = 0  # Default to 0 if the user is not logged in

    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            order = Order.objects.filter(customer=customer, complete=False).first()
            if order:
                cart_items_count = order.get_cart_items
        except Customer.DoesNotExist:
            pass  # No customer associated with this user

    context = {
        'products': products,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'store/shop.html', context)

# @login_required
def cart(request):
    customer = None
    items = []
    cart_total = 0
    cart_items_count = 0

    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            orders = Order.objects.filter(customer=customer, complete=False)
            orderItem = OrderItem.objects.all()

            if orders.exists():
                order = orders.first()
                items = order.orderitem_set.all()
                cart_total = order.get_cart_total
                cart_items_count = order.get_cart_items

                # Debugging output
                # print(f"Customer: {customer}")
                # print(f"Order: {order}")
                # print(f"Items: {items}")
                # print(f"Cart Total: {cart_total}")
                # print(f"Cart Items Count: {cart_items_count}")
            else:
                print("No incomplete orders found for the customer.")
        except Customer.DoesNotExist:
            print("No customer found for the user.")
    else:
        print("User is not authenticated.")

    context = {
        'items': items,
        'cart_total': cart_total,
        'cart_items_count': cart_items_count,
        'orderItem':orderItem
    }

    return render(request, 'store/cart.html', context)


def checkout(request):
    customer = None
    items = []
    cart_total = 0
    cart_items_count = 0

    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            orders = Order.objects.filter(customer=customer, complete=False)

            if orders.exists():
                order = orders.first()
                items = order.orderitem_set.all()
                cart_total = order.get_cart_total
                cart_items_count = order.get_cart_items

                # Debugging output
                # print(f"Customer: {customer}")
                # print(f"Order: {order}")
                # print(f"Items: {items}")
                # print(f"Cart Total: {cart_total}")
                # print(f"Cart Items Count: {cart_items_count}")
            else:
                print("No incomplete orders found for the customer.")
        except Customer.DoesNotExist:
            print("No customer found for the user.")
    else:
        print("User is not authenticated.")

    context = {
        'items': items,
        'cart_total': cart_total,
        'cart_items_count': cart_items_count
    }
    return render(request, 'store/checkout.html', context)



def update_cart(request):
    print("update_cart view triggered")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = unquote(data.get("name")).strip()  # Strip whitespace after decoding
            action = data.get("action")
            print('Request Body:', request.body)  # Ensure JSON is coming through
            print('Decoded Data:', data)          # Ensure data is correctly decoded
            print('Product Name:', product_name)  # Ensure product name is decoded correctly
            print('Action:', action)              # Ensure action is passed correctly
            
            # Check if the name and action are correct
            if not product_name or not action:
                return JsonResponse({'error': 'Missing product name or action'}, status=400)

            customer, _ = Customer.objects.get_or_create(user=request.user)
            
            print(f"Looking for product with name: '{product_name}'")
            
            # Case insensitive search and stripping any extra spaces
            try:
                product = Product.objects.get(name__iexact=product_name)
                print(f"Product found: {product}")
            except Product.DoesNotExist:
                return JsonResponse({"error": f"{product_name} doesn't exist."})

            order, _ = Order.objects.get_or_create(customer=customer, complete=False)
            orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

            if action == 'Increase':
                orderItem.quantity += 1
                # order.get_cart_items + 1
                orderItem.save()

            elif action == 'Decrease':
                if orderItem.quantity > 1:
                    orderItem.quantity -= 1
                    # order.get_cart_items + 1
                    orderItem.save()


                else:
                    orderItem.delete()
                    return JsonResponse({
                        'success': True,
                        'cart_items_count': order.get_cart_items,
                        'item_deleted': True,
                        'cart_total': order.get_cart_total,
                    })
            
            else:
                return JsonResponse({'error': "Invalid action"}, status=400)
            
            return JsonResponse({
                'success': True,
                'cart_items_count':order.get_cart_items,
                'new_item_quantity': orderItem.quantity,
                'item_total': orderItem.get_total,
                'cart_total': order.get_cart_total,
                'item_deleted': False,
                'item_name': product.name
            })        

        except Exception as e:
            print(f"Error in update_cart: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': "Invalid request method"}, status=400)
    
    # user authentication

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'store/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')  # Redirect to home page or dashboard
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')
