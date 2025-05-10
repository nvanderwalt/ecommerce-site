from django.shortcuts import render, redirect
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('product_list')
