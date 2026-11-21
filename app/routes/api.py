from flask import Blueprint, request, jsonify
from app.models.product import Product, Category
from app.routes.cart import get_cart_summary

api_bp = Blueprint('api', __name__)


@api_bp.route('/live-search')
def live_search():
    """Real-time autocomplete search returning products and categories."""
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'products': [], 'categories': []})

    products = Product.query.filter(
        Product.is_active == True,
        Product.name.ilike(f'%{q}%')
    ).limit(6).all()

    categories = Category.query.filter(
        Category.name.ilike(f'%{q}%')
    ).limit(3).all()

    product_list = [{
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'price': p.price,
        'price_formatted': f"₹{p.price:,.2f}",
        'image': p.primary_image_url,
        'category': p.category.name if p.category else 'Art Supplies',
        'badge': p.badge
    } for p in products]

    category_list = [{
        'id': c.id,
        'name': c.name,
        'slug': c.slug
    } for c in categories]

    return jsonify({
        'products': product_list,
        'categories': category_list
    })


@api_bp.route('/product/<int:id>/quick-view')
def quick_view(id):
    """Retrieve product details for modal quick view."""
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'category': product.category.name if product.category else '',
        'category_slug': product.category.slug if product.category else '',
        'price': product.price,
        'price_formatted': f"₹{product.price:,.2f}",
        'compare_at_price': product.compare_at_price,
        'compare_formatted': f"₹{product.compare_at_price:,.2f}" if product.compare_at_price else None,
        'discount_percent': product.discount_percent,
        'short_description': product.short_description or product.description[:180] + '...',
        'image_url': product.primary_image_url,
        'rating': product.rating,
        'reviews_count': product.reviews_count,
        'badge': product.badge,
        'in_stock': product.in_stock,
        'stock_quantity': product.stock_quantity,
        'brand': product.brand
    })


@api_bp.route('/cart/summary')
def cart_summary():
    """Retrieve current session cart stats for header badge and mini cart."""
    return jsonify(get_cart_summary())
