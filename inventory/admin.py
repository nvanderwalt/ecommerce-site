from django.contrib import admin
from .models import (
    Product, UserProfile, Review, Category, ExercisePlan, Exercise,
    ExerciseStep, ExercisePlanProgress, Cart, CartItem, NutritionPlan,
    NutritionMeal, NutritionPlanProgress
)

admin.site.register(Product)
admin.site.register(UserProfile)
admin.site.register(Review)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ExercisePlan)
class ExercisePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'price', 'duration_weeks')
    list_filter = ('category', 'difficulty')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'exercise_plan', 'sets', 'reps', 'rest_time')
    list_filter = ('exercise_plan',)
    search_fields = ('name', 'description')

@admin.register(ExerciseStep)
class ExerciseStepAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'order', 'duration_minutes')
    list_filter = ('plan',)
    search_fields = ('name', 'description')
    ordering = ('plan', 'order')

@admin.register(ExercisePlanProgress)
class ExercisePlanProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_completed', 'start_date')
    list_filter = ('is_completed', 'plan')
    search_fields = ('user__username', 'plan__name')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    list_filter = ('cart',)

@admin.register(NutritionPlan)
class NutritionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'diet_type', 'calories_per_day', 'price', 'is_active')
    list_filter = ('diet_type', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(NutritionMeal)
class NutritionMealAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'meal_type', 'calories', 'order')
    list_filter = ('plan', 'meal_type')
    search_fields = ('name', 'description')
    ordering = ('plan', 'order')

@admin.register(NutritionPlanProgress)
class NutritionPlanProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_completed', 'start_date')
    list_filter = ('is_completed', 'plan')
    search_fields = ('user__username', 'plan__name')
