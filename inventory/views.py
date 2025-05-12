from django.shortcuts import render, redirect
from .models import Product, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, ReviewForm
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def product_list(request):
    products = Product.objects.all()
    form = ReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        product_id = request.POST.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                return redirect('product_list')
        except Product.DoesNotExist:
            pass  # Optionally add logging or an error message

    return render(request, 'inventory/product_list.html', {
        'products': products,
        'form': form,
    })

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('product_list')

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'inventory/cart.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@csrf_exempt
@login_required
def create_checkout_session(request):
    cart = request.session.get('cart', {})
    line_items = []

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': quantity,
            })
        except Product.DoesNotExist:
            pass

    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:8000/success/',
        cancel_url='http://127.0.0.1:8000/cart/',
    )

    return JsonResponse({'id': session.id})

def payment_success(request):
    return render(request, 'inventory/payment_success.html')

def payment_cancel(request):
    return render(request, 'inventory/payment_cancel.html')

@login_required
def profile_view(request):
    profile = request.user.userprofile
    posts = request.user.post_set.order_by('-created_at')  # fetch user's posts

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'inventory/profile.html', {
        'form': form,
        'posts': posts,
    })

def error_view(request):
    return render(request, 'error.html')
