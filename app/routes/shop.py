from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import current_user
from app.models.product import Category, Product, Review, Wishlist
from app.extensions import db

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/')
def catalog():
    """Main catalog browsing with multi-faceted filtering, searching, and sorting."""
    # Query parameters
    search_query = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    badge_filter = request.args.get('badge', '').strip()
    in_stock_only = request.args.get('in_stock', type=bool)
    sort_by = request.args.get('sort', 'featured')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Base query for active products
    query = Product.query.filter_by(is_active=True)

    # Search filter
    if search_query:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search_query}%'),
                Product.description.ilike(f'%{search_query}%'),
                Product.short_description.ilike(f'%{search_query}%'),
                Product.brand.ilike(f'%{search_query}%'),
                Product.tags.ilike(f'%{search_query}%')
            )
        )

    # Category filter
    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)

    # Price range filter
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Badge filter
    if badge_filter:
        query = query.filter(Product.badge == badge_filter)

    # Stock filter
    if in_stock_only:
        query = query.filter(Product.stock_quantity > 0)

    # Sorting
    if sort_by == 'price-asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price-desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc(), Product.reviews_count.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    elif sort_by == 'discount':
        query = query.order_by((Product.compare_at_price - Product.price).desc())
    else:  # 'featured'
        query = query.order_by(Product.is_featured.desc(), Product.is_bestseller.desc(), Product.id.asc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    # Categories list for sidebar
    categories = Category.query.order_by(Category.name.asc()).all()

    # Collect wishlist IDs for current user to show active heart icon
    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = {w.product_id for w in current_user.wishlist_items.all()}

    return render_template(
        'shop/catalog.html',
        products=products,
        pagination=pagination,
        categories=categories,
        selected_category=selected_category,
        search_query=search_query,
        min_price=min_price,
        max_price=max_price,
        badge_filter=badge_filter,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
        user_wishlist_ids=user_wishlist_ids
    )


@shop_bp.route('/category/<slug>')
def category(slug):
    """Specific category showcase with curated overview and category products."""
    cat = Category.query.filter_by(slug=slug).first_or_404()
    
    # Sub-query for this category's products
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'featured')
    
    query = Product.query.filter_by(category_id=cat.id, is_active=True)
    
    if sort_by == 'price-asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price-desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.is_featured.desc(), Product.id.asc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    
    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = {w.product_id for w in current_user.wishlist_items.all()}

    return render_template(
        'shop/category.html',
        category=cat,
        products=pagination.items,
        pagination=pagination,
        sort_by=sort_by,
        user_wishlist_ids=user_wishlist_ids
    )


@shop_bp.route('/product/<slug>', methods=['GET', 'POST'])
def detail(slug):
    """Detailed product presentation with image gallery, specs, customer reviews, and related items."""
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Handle customer review submission
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please log in to submit a verified product review.', 'warning')
            return redirect(url_for('auth.login', next=request.path))

        rating = request.form.get('rating', 5, type=int)
        reviewer_title = request.form.get('title', '').strip()
        comment = request.form.get('comment', '').strip()

        if not comment:
            flash('Please enter your review comments.', 'danger')
        else:
            review = Review(
                product_id=product.id,
                user_id=current_user.id,
                rating=max(1, min(5, rating)),
                reviewer_name=current_user.name,
                reviewer_title=reviewer_title or 'Verified Artist',
                comment=comment,
                verified_buyer=True
            )
            db.session.add(review)
            db.session.commit()
            product.update_rating()
            db.session.commit()

            flash('Thank you! Your artist review has been published.', 'success')
            return redirect(url_for('shop.detail', slug=product.slug))

    # Related products from same category
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()

    # User wishlist status
    is_in_wishlist = False
    if current_user.is_authenticated:
        is_in_wishlist = current_user.has_in_wishlist(product.id)

    # Product reviews sorted newest first
    reviews = product.reviews.order_by(Review.created_at.desc()).all()

    return render_template(
        'shop/detail.html',
        product=product,
        reviews=reviews,
        related_products=related_products,
        is_in_wishlist=is_in_wishlist
    )


@shop_bp.route('/bestsellers')
def bestsellers():
    """Direct route for top-rated bestseller art essentials."""
    return redirect(url_for('shop.catalog', badge='Bestseller'))


@shop_bp.route('/combos')
def combos():
    """Direct route for curated kits and bundles."""
    combos_cat = Category.query.filter(Category.name.ilike('%Combos%')).first()
    if combos_cat:
        return redirect(url_for('shop.category', slug=combos_cat.slug))
    return redirect(url_for('shop.catalog', q='Combo'))
