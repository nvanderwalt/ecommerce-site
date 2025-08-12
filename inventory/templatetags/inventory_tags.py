from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return ''

@register.simple_tag
def get_nutrition_icon(diet_type):
    """
    Returns appropriate FontAwesome icon class for each diet type
    """
    icon_map = {
        'VEG': 'fas fa-leaf',  # Leaf for vegetarian
        'VEGAN': 'fas fa-seedling',  # Seedling for vegan
        'PALEO': 'fas fa-drumstick-bite',  # Drumstick for paleo
        'KETO': 'fas fa-fire',  # Fire for ketogenic (burning fat)
        'BAL': 'fas fa-balance-scale',  # Balance scale for balanced diet
    }
    
    return icon_map.get(diet_type, 'fas fa-apple-alt')  # Default to apple if not found

@register.simple_tag
def get_nutrition_color(diet_type):
    """
    Returns appropriate color class for each diet type
    """
    color_map = {
        'VEG': '#28a745',  # Green for vegetarian
        'VEGAN': '#20c997',  # Teal for vegan
        'PALEO': '#fd7e14',  # Orange for paleo
        'KETO': '#dc3545',  # Red for ketogenic
        'BAL': '#007bff',  # Blue for balanced
    }
    
    return color_map.get(diet_type, '#28a745')  # Default to green if not found

@register.filter
def get_exercise_plan(plan_id):
    """
    Get exercise plan by ID
    """
    from inventory.models import ExercisePlan
    try:
        return ExercisePlan.objects.get(id=plan_id)
    except ExercisePlan.DoesNotExist:
        return None

@register.filter
def get_nutrition_plan(plan_id):
    """
    Get nutrition plan by ID
    """
    from inventory.models import NutritionPlan
    try:
        return NutritionPlan.objects.get(id=plan_id)
    except NutritionPlan.DoesNotExist:
        return None

@register.filter
def get_exercise_progress(plan, user):
    """
    Get exercise progress for a plan and user
    """
    from inventory.models import ExercisePlanProgress
    try:
        return ExercisePlanProgress.objects.get(plan=plan, user=user)
    except ExercisePlanProgress.DoesNotExist:
        return None

@register.filter
def get_nutrition_progress(plan, user):
    """
    Get nutrition progress for a plan and user
    """
    from inventory.models import NutritionPlanProgress
    try:
        return NutritionPlanProgress.objects.get(plan=plan, user=user)
    except NutritionPlanProgress.DoesNotExist:
        return None

@register.filter
def add_days(date, days):
    """
    Add days to a date
    """
    from datetime import timedelta
    if date and days:
        try:
            return date + timedelta(days=int(days))
        except (ValueError, TypeError):
            return date
    return date

@register.filter
def multiply(value, arg):
    """
    Multiply value by arg
    """
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    """
    Divide value by arg
    """
    try:
        return int(value) / int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def ceil(value):
    """
    Ceiling function
    """
    import math
    try:
        return math.ceil(float(value))
    except (ValueError, TypeError):
        return value 