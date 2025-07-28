from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from inventory.models import Product, ExercisePlan, NutritionPlan
from posts.models import Post


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return [
            'product_list',
            'exercise_plan_list',
            'register',
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at


class ExercisePlanSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return ExercisePlan.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at


class NutritionPlanSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return NutritionPlan.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at


class PostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at 