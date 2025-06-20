# Generated by Django 5.2.1 on 2025-06-03 12:14

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='inventory.category')),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ExercisePlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duration_weeks', models.IntegerField(blank=True, null=True)),
                ('difficulty', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='exercise_plans/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('sets', models.IntegerField()),
                ('reps', models.IntegerField()),
                ('rest_time', models.IntegerField(help_text='Rest time in seconds')),
                ('exercise_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='inventory.exerciseplan')),
            ],
        ),
        migrations.CreateModel(
            name='ExerciseStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('duration_minutes', models.PositiveIntegerField(default=5)),
                ('sets', models.PositiveIntegerField(default=1)),
                ('reps', models.PositiveIntegerField(default=10)),
                ('rest_minutes', models.PositiveIntegerField(default=1)),
                ('video_url', models.URLField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='exercise_steps/')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='inventory.exerciseplan')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('plan', 'order')},
            },
        ),
        migrations.CreateModel(
            name='NutritionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField()),
                ('diet_type', models.CharField(choices=[('VEG', 'Vegetarian'), ('VEGAN', 'Vegan'), ('PALEO', 'Paleo'), ('KETO', 'Ketogenic'), ('BAL', 'Balanced')], max_length=5)),
                ('calories_per_day', models.PositiveIntegerField(help_text='Target calories per day')),
                ('protein_grams', models.PositiveIntegerField(help_text='Target protein in grams')),
                ('carbs_grams', models.PositiveIntegerField(help_text='Target carbs in grams')),
                ('fat_grams', models.PositiveIntegerField(help_text='Target fat in grams')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, default=29.99, max_digits=10)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('nutritionist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NutritionMeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('meal_type', models.CharField(choices=[('BRK', 'Breakfast'), ('LUN', 'Lunch'), ('DIN', 'Dinner'), ('SNK', 'Snack')], max_length=3)),
                ('calories', models.PositiveIntegerField()),
                ('protein_grams', models.PositiveIntegerField()),
                ('carbs_grams', models.PositiveIntegerField()),
                ('fat_grams', models.PositiveIntegerField()),
                ('ingredients', models.TextField()),
                ('instructions', models.TextField()),
                ('prep_time_minutes', models.PositiveIntegerField(default=15)),
                ('cooking_time_minutes', models.PositiveIntegerField(default=30)),
                ('image', models.ImageField(blank=True, null=True, upload_to='nutrition_meals/')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meals', to='inventory.nutritionplan')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('plan', 'order')},
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('stock', models.PositiveIntegerField(default=0)),
                ('sku', models.CharField(max_length=50, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='inventory.category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goal', models.CharField(blank=True, max_length=255)),
                ('fitness_level', models.CharField(blank=True, max_length=50)),
                ('dietary_preference', models.CharField(blank=True, max_length=100)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('address_line1', models.CharField(blank=True, max_length=255)),
                ('address_line2', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExercisePlanProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.exerciseplan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('completed_steps', models.ManyToManyField(related_name='completed_by', to='inventory.exercisestep')),
                ('current_step', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.exercisestep')),
            ],
            options={
                'unique_together': {('user', 'plan')},
            },
        ),
        migrations.CreateModel(
            name='NutritionPlanProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('completed_meals', models.ManyToManyField(related_name='completed_by', to='inventory.nutritionmeal')),
                ('current_meal', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.nutritionmeal')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.nutritionplan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'plan')},
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product')),
            ],
            options={
                'unique_together': {('cart', 'product')},
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='inventory.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('product', 'user')},
            },
        ),
    ]
