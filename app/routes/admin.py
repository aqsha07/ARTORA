from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from app.models.user import User
from app.models.product import Category, Product, ProductImage, slugify
from app.models.order import Order
from app.extensions import db

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator ensuring that only authenticated admin users can access the endpoint."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin authorization required to access the ARTORA Curator Panel.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard overview: key metrics, low inventory alerts, and recent orders."""
    total_sales = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0.0
    total_orders = Order.query.count()
    total_products = Product.query.count()
    total_customers = User.query.filter_by(role='user').count()

    # Low stock items (< 15 units remaining)
    low_stock_products = Product.query.filter(Product.stock_quantity <= 15).order_by(Product.stock_quantity.asc()).all()

    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()

    return render_template(
        'admin/dashboard.html',
        total_sales=total_sales,
        total_orders=total_orders,
        total_products=total_products,
        total_customers=total_customers,
        low_stock_products=low_stock_products,
        recent_orders=recent_orders
    )


@admin_bp.route('/products')
@admin_required
def products():
    """Product catalog management table."""
    search = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)

    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)

    products = query.order_by(Product.id.desc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template('admin/products.html', products=products, categories=categories, search=search, selected_category_id=category_id)


@admin_bp.route('/products/new', methods=['GET', 'POST'])
@admin_required
def product_new():
    """Create a new product listing."""
    categories = Category.query.order_by(Category.name.asc()).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        compare_at_price = request.form.get('compare_at_price', type=float) or None
        stock_quantity = request.form.get('stock_quantity', 50, type=int)
        badge = request.form.get('badge', '').strip() or None
        brand = request.form.get('brand', 'ARTORA Studio').strip()
        short_desc = request.form.get('short_description', '').strip()
        description = request.form.get('description', '').strip()
        specifications = request.form.get('specifications', '').strip()
        image_url = request.form.get('image_url', '').strip()
        is_featured = bool(request.form.get('is_featured'))
        is_bestseller = bool(request.form.get('is_bestseller'))

        if not name or not category_id or price is None or not description:
            flash('Please fill in all mandatory fields.', 'danger')
        else:
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while Product.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

            product = Product(
                name=name,
                slug=slug,
                category_id=category_id,
                price=price,
                compare_at_price=compare_at_price,
                stock_quantity=stock_quantity,
                badge=badge,
                brand=brand,
                short_description=short_desc,
                description=description,
                specifications=specifications,
                is_featured=is_featured,
                is_bestseller=is_bestseller,
                is_active=True
            )
            db.session.add(product)
            db.session.flush()

            # Add primary product image
            if image_url:
                img = ProductImage(
                    product_id=product.id,
                    image_url=image_url,
                    alt_text=product.name,
                    is_primary=True
                )
                db.session.add(img)

            db.session.commit()
            flash(f'Product "{product.name}" created successfully.', 'success')
            return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', product=None, categories=categories, title="Add New Product")


@admin_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def product_edit(id):
    """Edit existing product listing."""
    product = Product.query.get_or_404(id)
    categories = Category.query.order_by(Category.name.asc()).all()

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.category_id = request.form.get('category_id', type=int)
        product.price = request.form.get('price', type=float)
        product.compare_at_price = request.form.get('compare_at_price', type=float) or None
        product.stock_quantity = request.form.get('stock_quantity', 0, type=int)
        product.badge = request.form.get('badge', '').strip() or None
        product.brand = request.form.get('brand', 'ARTORA Studio').strip()
        product.short_description = request.form.get('short_description', '').strip()
        product.description = request.form.get('description', '').strip()
        product.specifications = request.form.get('specifications', '').strip()
        product.is_featured = bool(request.form.get('is_featured'))
        product.is_bestseller = bool(request.form.get('is_bestseller'))
        product.is_active = bool(request.form.get('is_active'))

        image_url = request.form.get('image_url', '').strip()
        if image_url:
            primary_img = product.images.filter_by(is_primary=True).first()
            if primary_img:
                primary_img.image_url = image_url
            else:
                img = ProductImage(product_id=product.id, image_url=image_url, is_primary=True)
                db.session.add(img)

        db.session.commit()
        flash(f'Product "{product.name}" updated successfully.', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', product=product, categories=categories, title=f"Edit {product.name}")


@admin_bp.route('/products/<int:id>/delete', methods=['POST'])
@admin_required
def product_delete(id):
    """Delete a product."""
    product = Product.query.get_or_404(id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{name}" has been removed.', 'info')
    return redirect(url_for('admin.products'))


@admin_bp.route('/categories')
@admin_required
def categories():
    """View and manage categories."""
    categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/orders')
@admin_required
def orders():
    """View all customer orders with filtering by status."""
    status_filter = request.args.get('status', '').strip()
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)


@admin_bp.route('/orders/<int:id>', methods=['GET', 'POST'])
@admin_required
def order_detail(id):
    """View order details and update shipping/processing status."""
    order = Order.query.get_or_404(id)

    if request.method == 'POST':
        new_status = request.form.get('status')
        tracking_number = request.form.get('tracking_number', '').strip()
        courier_name = request.form.get('courier_name', '').strip()

        if new_status:
            order.status = new_status
        if tracking_number:
            order.tracking_number = tracking_number
        if courier_name:
            order.courier_name = courier_name

        db.session.commit()
        flash(f'Order {order.order_number} status updated to "{order.status}".', 'success')
        return redirect(url_for('admin.order_detail', id=order.id))

    return render_template('admin/order_detail.html', order=order)
