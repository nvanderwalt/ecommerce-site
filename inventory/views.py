from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, UserProfile, ExercisePlan
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, ReviewForm
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

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

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = ReviewForm()
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', slug=slug)
    
    return render(request, 'inventory/product_detail.html', {
        'product': product,
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

@login_required
@csrf_exempt
def create_checkout_session(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    stripe.api_key = settings.STRIPE_SECRET_KEY
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
                        'description': product.description[:100],
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': quantity,
            })
        except Product.DoesNotExist:
            pass

    if not line_items:
        messages.error(request, "Your cart is empty.")
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cart/'),
            metadata={
                'type': 'cart_checkout'
            }
        )
        return JsonResponse({'id': session.id})
    except stripe.error.AuthenticationError as e:
        return JsonResponse({'error': 'Authentication failed'}, status=401)
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Server error'}, status=500)

def payment_success(request):
    # Clear the cart if it was a cart checkout
    if request.session.get('cart'):
        request.session['cart'] = {}
    messages.success(request, "Payment successful! Thank you for your purchase.")
    return redirect('product_list')

def payment_cancel(request):
    messages.info(request, "Your payment was cancelled. Please try again when you're ready.")
    return redirect('cart')

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

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        try:
            product = Product.objects.get(id=product_id)
            if action == 'increase':
                cart[product_id_str] = cart.get(product_id_str, 0) + 1
                messages.success(request, f'Added another {product.name} to your cart.')
            elif action == 'decrease':
                if cart.get(product_id_str, 0) > 1:
                    cart[product_id_str] = cart[product_id_str] - 1
                    messages.success(request, f'Reduced quantity of {product.name} in your cart.')
                else:
                    messages.warning(request, f'Quantity cannot be less than 1.')
            
            request.session['cart'] = cart
            
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
    
    return redirect('cart')

@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        try:
            product = Product.objects.get(id=product_id)
            if product_id_str in cart:
                del cart[product_id_str]
                request.session['cart'] = cart
                messages.success(request, f'Removed {product.name} from your cart.')
            else:
                messages.warning(request, "This item wasn't in your cart.")
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
    
    return redirect('cart')

@login_required
def exercise_plan_list(request):
    plans = ExercisePlan.objects.all()
    
    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty:
        plans = plans.filter(difficulty=difficulty)
    
    # Filter by max duration
    max_duration = request.GET.get('max_duration')
    if max_duration:
        plans = plans.filter(duration_minutes__lte=int(max_duration))
    
    return render(request, 'inventory/exercise_plans.html', {
        'plans': plans
    })

@login_required
def exercise_plan_detail(request, plan_id):
    try:
        plan = ExercisePlan.objects.get(id=plan_id)
        return render(request, 'inventory/exercise_plan_detail.html', {
            'plan': plan,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        })
    except ExercisePlan.DoesNotExist:
        messages.error(request, "Exercise plan not found.")
        return redirect('exercise_plan_list')

@csrf_exempt
@login_required
def create_plan_checkout_session(request, plan_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        plan = ExercisePlan.objects.get(id=plan_id)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': plan.name,
                        'description': f"{plan.get_difficulty_display()} level, {plan.duration_minutes} minutes"
                    },
                    'unit_amount': int(plan.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri(f'/exercise-plan/{plan_id}/'),
            metadata={
                'type': 'plan_checkout',
                'plan_id': str(plan_id)
            }
        )

        return JsonResponse({'id': session.id})
    except ExercisePlan.DoesNotExist:
        return JsonResponse({'error': 'Exercise plan not found'}, status=404)
    except stripe.error.AuthenticationError:
        return JsonResponse({'error': 'Authentication failed'}, status=401)
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Server error'}, status=500)
