from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from app.models.product import Category, Product, Review, Wishlist
from app.extensions import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage: showcases featured categories, trending supplies, bestsellers,
    special offers, artist starter kits, and customer testimonials."""
    # 1. All 11 art supply categories
    categories = Category.query.order_by(Category.display_order.asc()).all()

    # 2. Trending Art Supplies (Top rated & highly reviewed)
    trending_products = Product.query.filter_by(is_active=True)\
        .order_by(Product.rating.desc(), Product.reviews_count.desc(), Product.id.asc())\
        .limit(8).all()

    # 3. Bestselling Products
    bestsellers = Product.query.filter_by(is_active=True, is_bestseller=True).limit(8).all()
    if not bestsellers or len(bestsellers) < 4:
        bestsellers = Product.query.filter_by(is_active=True)\
            .filter(Product.badge.in_(['Bestseller', 'Artisan Choice']))\
            .limit(8).all()

    # 4. Artist Starter Kits & Combos
    kits_cat = Category.query.filter(Category.name.ilike('%Kits%')).first()
    starter_kits = kits_cat.products.filter_by(is_active=True).all() if kits_cat else []
    if not starter_kits:
        starter_kits = Product.query.filter_by(is_active=True)\
            .filter(Product.name.ilike('%Kit%') | Product.name.ilike('%Chest%') | Product.name.ilike('%Suite%'))\
            .limit(4).all()

    # 5. Special Offers & Discounts (Products with prominent savings)
    special_deals = Product.query.filter(
        Product.is_active == True,
        Product.compare_at_price > Product.price
    ).order_by((Product.compare_at_price - Product.price).desc()).limit(4).all()

    # 6. Customer Testimonials & Reviews
    featured_reviews = Review.query.filter_by(rating=5).order_by(Review.created_at.desc()).limit(3).all()

    # 7. Current user wishlist IDs for heart state toggles
    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = {w.product_id for w in current_user.wishlist_items.all()}

    return render_template(
        'main/index.html',
        categories=categories,
        trending_products=trending_products,
        bestsellers=bestsellers,
        starter_kits=starter_kits,
        special_deals=special_deals,
        featured_reviews=featured_reviews,
        user_wishlist_ids=user_wishlist_ids
    )


@main_bp.route('/about')
def about():
    """About ARTORA: Brand philosophy, material sourcing, artisan studio commitment."""
    return render_template('main/about.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with interactive inquiry form."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('Please complete all required fields.', 'danger')
        else:
            flash(f'Thank you, {name}! Your message regarding "{subject or "Art Inquiry"}" has been sent to our studio curators. We will reply within 24 hours.', 'success')
            return redirect(url_for('main.contact'))

    return render_template('main/contact.html')


@main_bp.route('/faq')
def faq():
    """Frequently Asked Questions: Surfaces, paper weights, paints, brush care, and ordering."""
    return render_template('main/faq.html')


@main_bp.route('/shipping')
def shipping():
    """Shipping, delivery timelines, packaging safety, and 30-day return policies."""
    return render_template('main/shipping.html')
