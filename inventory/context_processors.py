def cart_count(request):
    """Context processor to provide cart count to all templates."""
    cart = request.session.get('cart', {})
    # Sum up all quantities instead of counting unique items
    total_items = sum(cart.values())
    return {'cart_count': total_items} 