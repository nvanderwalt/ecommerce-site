from django.contrib import admin
from .models import Product, UserProfile, Review, Category, ExercisePlan, Exercise

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
