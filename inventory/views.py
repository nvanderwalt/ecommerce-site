from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, UserProfile, ExercisePlan, NutritionPlan, NutritionPlanProgress, NutritionMeal, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, ReviewForm
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.core.mail import send_mail

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
    """Create a Stripe checkout session for a nutrition plan."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        plan = NutritionPlan.objects.get(id=plan_id, is_active=True)
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan.name,
                        'description': f"{plan.get_diet_type_display()} - {plan.calories_per_day} calories/day",
                    },
                    'unit_amount': int(plan.current_price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('inventory:nutrition_plan_detail', args=[plan.id])),
            cancel_url=request.build_absolute_uri(reverse('inventory:nutrition_plan_list')),
            client_reference_id=str(plan.id),
            customer_email=request.user.email,
        )
        
        return JsonResponse({'id': session.id})
    except NutritionPlan.DoesNotExist:
        return JsonResponse({'error': 'Plan not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def nutrition_plan_list(request):
    """View for listing nutrition plans with filtering."""
    plans = NutritionPlan.objects.filter(is_active=True)
    
    # Filter by diet type
    diet_type = request.GET.get('diet_type')
    if diet_type:
        plans = plans.filter(diet_type=diet_type)
    
    # Filter by max calories
    max_calories = request.GET.get('max_calories')
    if max_calories:
        plans = plans.filter(calories_per_day__lte=int(max_calories))
    
    return render(request, 'inventory/nutrition_plans.html', {
        'plans': plans
    })

@login_required
def nutrition_plan_detail(request, plan_id):
    """View for displaying nutrition plan details."""
    plan = get_object_or_404(NutritionPlan, id=plan_id, is_active=True)
    meals = plan.meals.all().order_by('order')
    
    # Get progress if user has started the plan
    progress = None
    if request.user.is_authenticated:
        progress = NutritionPlanProgress.objects.filter(
            user=request.user,
            plan=plan
        ).first()
    
    # Get meal type progress
    meal_types = []
    if progress:
        for meal_type, _ in NutritionMeal.MEAL_TYPE_CHOICES:
            total_meals = meals.filter(meal_type=meal_type).count()
            completed_meals = progress.completed_meals.filter(meal_type=meal_type).count()
            percentage = (completed_meals / total_meals * 100) if total_meals > 0 else 0
            meal_types.append((meal_type, dict(NutritionMeal.MEAL_TYPE_CHOICES)[meal_type], percentage))
    
    return render(request, 'inventory/nutrition_plan_detail.html', {
        'plan': plan,
        'meals': meals,
        'progress': progress,
        'meal_types': meal_types,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@login_required
def complete_meal(request, plan_id, meal_id):
    """View for marking a meal as completed."""
    if request.method != 'POST':
        return redirect('inventory:nutrition_plan_detail', plan_id=plan_id)
    
    plan = get_object_or_404(NutritionPlan, id=plan_id)
    meal = get_object_or_404(NutritionMeal, id=meal_id, plan=plan)
    
    # Get or create progress
    progress, created = NutritionPlanProgress.objects.get_or_create(
        user=request.user,
        plan=plan,
        defaults={'current_meal': meal}
    )
    
    # Complete the meal
    progress.complete_meal(meal)
    
    # Check if all meals are completed
    if progress.completed_meals.count() == plan.meals.count():
        progress.is_completed = True
        progress.completion_date = timezone.now()
        progress.save()
    
    messages.success(request, f'Marked {meal.name} as completed!')
    return redirect('inventory:nutrition_plan_detail', plan_id=plan_id)

class ExercisePlanListView(ListView):
    model = ExercisePlan
    template_name = 'inventory/exercise_plan_list.html'
    context_object_name = 'exercise_plans'
    paginate_by = 9

    def get_queryset(self):
        queryset = ExercisePlan.objects.all()
        category = self.request.GET.get('category')
        difficulty = self.request.GET.get('difficulty')
        
        if category:
            queryset = queryset.filter(category__slug=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['difficulties'] = ExercisePlan.DIFFICULTY_CHOICES
        return context

class ExercisePlanDetailView(DetailView):
    model = ExercisePlan
    template_name = 'inventory/exercise_plan_detail.html'
    context_object_name = 'exercise_plan'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercises'] = self.object.exercises.all()
        return context

def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # In a real application, you would save this to a database
            # and integrate with an email marketing service
            try:
                send_mail(
                    'Welcome to FitFusion Newsletter!',
                    'Thank you for subscribing to our newsletter. We\'ll keep you updated with the latest fitness tips and offers.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            except Exception as e:
                messages.error(request, 'There was an error processing your subscription. Please try again.')
        else:
            messages.error(request, 'Please provide a valid email address.')
    return redirect('home')
