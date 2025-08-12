from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    goal = models.CharField(max_length=255, blank=True)
    fitness_level = models.CharField(max_length=50, blank=True)
    dietary_preference = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update user profile when a User is created or updated."""
    UserProfile.objects.get_or_create(user=instance)

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"Review by {self.user.username} - {self.rating}★"

class ExercisePlan(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_weeks = models.IntegerField(null=True, blank=True)
    daily_exercise_minutes = models.PositiveIntegerField(default=30, help_text="Minutes of exercise per day")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='exercise_plans/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Set daily exercise minutes based on difficulty
        if self.difficulty == 'beginner':
            self.daily_exercise_minutes = 30
        elif self.difficulty == 'intermediate':
            self.daily_exercise_minutes = 50
        elif self.difficulty == 'advanced':
            self.daily_exercise_minutes = 90
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

class Exercise(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    sets = models.IntegerField()
    reps = models.IntegerField()
    rest_time = models.IntegerField(help_text="Rest time in seconds")
    exercise_plan = models.ForeignKey(ExercisePlan, related_name='exercises', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class ExerciseStep(models.Model):
    """Represents a single exercise step within a workout plan."""
    plan = models.ForeignKey(ExercisePlan, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(default=5)
    sets = models.PositiveIntegerField(default=1)
    reps = models.PositiveIntegerField(default=10)
    rest_minutes = models.PositiveIntegerField(default=1)
    video_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='exercise_steps/', blank=True, null=True)

    class Meta:
        ordering = ['order']
        unique_together = ['plan', 'order']

    def __str__(self):
        return f"{self.plan.name} - Step {self.order}: {self.name}"

class ExercisePlanProgress(models.Model):
    """Tracks user progress through exercise plans."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(ExercisePlan, on_delete=models.CASCADE)
    current_step = models.ForeignKey(ExerciseStep, on_delete=models.SET_NULL, null=True)
    completed_steps = models.ManyToManyField(ExerciseStep, related_name='completed_by')
    start_date = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'plan']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} Progress"

    def complete_step(self, step):
        """Mark a step as completed and update progress."""
        if step.plan == self.plan:
            self.completed_steps.add(step)
            self.last_activity = timezone.now()
            self.save()

    def get_progress_percentage(self):
        """Calculate progress percentage."""
        total_steps = self.plan.steps.count()
        if total_steps == 0:
            return 0
        completed = self.completed_steps.count()
        return (completed / total_steps) * 100

    def get_end_date(self):
        """Calculate the expected end date based on plan duration."""
        if self.plan.duration_weeks:
            from datetime import timedelta
            return self.start_date + timedelta(weeks=self.plan.duration_weeks)
        return None

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} - {self.user.username if self.user else 'Anonymous'}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.product.current_price

class NutritionPlan(models.Model):
    DIET_TYPE_CHOICES = [
        ('VEG', 'Vegetarian'),
        ('VEGAN', 'Vegan'),
        ('PALEO', 'Paleo'),
        ('KETO', 'Ketogenic'),
        ('BAL', 'Balanced'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    diet_type = models.CharField(max_length=5, choices=DIET_TYPE_CHOICES)
    calories_per_day = models.PositiveIntegerField(help_text="Target calories per day")
    protein_grams = models.PositiveIntegerField(help_text="Target protein in grams")
    carbs_grams = models.PositiveIntegerField(help_text="Target carbs in grams")
    fat_grams = models.PositiveIntegerField(help_text="Target fat in grams")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    nutritionist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=29.99)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_diet_type_display()}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price

class NutritionMeal(models.Model):
    MEAL_TYPE_CHOICES = [
        ('BRK', 'Breakfast'),
        ('LUN', 'Lunch'),
        ('DIN', 'Dinner'),
        ('SNK', 'Snack'),
    ]
    
    plan = models.ForeignKey(NutritionPlan, on_delete=models.CASCADE, related_name='meals')
    order = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=200)
    description = models.TextField()
    meal_type = models.CharField(max_length=3, choices=MEAL_TYPE_CHOICES)
    calories = models.PositiveIntegerField()
    protein_grams = models.PositiveIntegerField()
    carbs_grams = models.PositiveIntegerField()
    fat_grams = models.PositiveIntegerField()
    ingredients = models.TextField()
    instructions = models.TextField()
    prep_time_minutes = models.PositiveIntegerField(default=15)
    cooking_time_minutes = models.PositiveIntegerField(default=30)
    image = models.ImageField(upload_to='nutrition_meals/', blank=True, null=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['plan', 'order']
    
    def __str__(self):
        return f"{self.plan.name} - {self.get_meal_type_display()}: {self.name}"

class NutritionPlanProgress(models.Model):
    """Tracks user progress through nutrition plans."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(NutritionPlan, on_delete=models.CASCADE)
    current_meal = models.ForeignKey(NutritionMeal, on_delete=models.SET_NULL, null=True)
    completed_meals = models.ManyToManyField(NutritionMeal, related_name='completed_by')
    start_date = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'plan']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} Progress"
    
    def complete_meal(self, meal):
        """Mark a meal as completed and update progress."""
        if meal.plan == self.plan:
            self.completed_meals.add(meal)
            self.last_activity = timezone.now()
            self.save()
    
    def get_progress_percentage(self):
        """Calculate progress percentage."""
        total_meals = self.plan.meals.count()
        if total_meals == 0:
            return 0
        completed = self.completed_meals.count()
        return (completed / total_meals) * 100

    def get_end_date(self):
        """Calculate the expected end date based on meal count (assuming 3 meals per day)."""
        total_meals = self.plan.meals.count()
        if total_meals > 0:
            from datetime import timedelta
            import math
            days_needed = math.ceil(total_meals / 3)  # 3 meals per day
            return self.start_date + timedelta(days=days_needed)
        return None
