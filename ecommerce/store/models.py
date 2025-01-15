from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm
import uuid



# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True )
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True)

    def __str__(self):
        return self.name if self.name else (self.user.username if self.user else "Unnamed Customer")    
class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=True )
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return str(self.name)
    

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True,blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, editable=False, blank=False)


    def __str__(self):
        return f"Order {self.transaction_id or 'No Transaction ID'}"
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            while True:
                new_id = str(uuid.uuid4())
                if not Order.objects.filter(transaction_id=new_id).exists():
                    self.transaction_id = new_id
                    break
        super().save(*args, **kwargs)

    @property
    def get_cart_total(self):
        OrderItems = self.orderitem_set.all()
        total = sum([item.get_total for item in OrderItems])
        return total
    
    @property
    def get_cart_items(self):
        OrderItems = self.orderitem_set.all()
        total =  sum([item.quantity for item in OrderItems])
        return total
    


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)    
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.product.name)
    
    @property
    def get_total(self):
        return self.quantity * self.product.price
    
class ShippingInformation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.customer.name} - {self.address}" if self.customer.name and self.address else (self.customer.user.username if self.customer.user else "Unnamed Customer")

    
class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    shipping_info = models.ForeignKey(ShippingInformation, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  f"{self.customer.name} - ${self.amount}" if self.customer.name and self.amount else (self.customer.user.username if self.customer.user else "Unnamed Customer")




