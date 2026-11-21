from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, Address
from app.models.product import Product, Wishlist
from app.models.order import Order
from app.extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User and Administrator authentication."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name}!', 'success')

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('auth.profile'))
        else:
            flash('Invalid email address or password. Please try again.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('Please fill in all mandatory fields.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in.', 'warning')
        else:
            user = User(
                name=name,
                email=email,
                phone=phone,
                role='user'
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash('Welcome to the ARTORA collective! Your artist account has been created.', 'success')
            return redirect(url_for('auth.profile'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout current user."""
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Customer dashboard: profile details, order history, addresses, and wishlist."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()

        if name:
            current_user.name = name
            current_user.phone = phone
            current_user.bio = bio
            db.session.commit()
            flash('Your artist profile has been updated.', 'success')
        return redirect(url_for('auth.profile'))

    # Load orders for this user
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    wishlist_items = current_user.wishlist_items.all()
    addresses = current_user.addresses.all()

    return render_template(
        'auth/profile.html',
        user=current_user,
        orders=orders,
        wishlist_items=wishlist_items,
        addresses=addresses
    )


@auth_bp.route('/wishlist')
@login_required
def wishlist():
    """Dedicated wishlist gallery."""
    wishlist_items = current_user.wishlist_items.all()
    return render_template('auth/wishlist.html', wishlist_items=wishlist_items)


@auth_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST', 'GET'])
def toggle_wishlist(product_id):
    """Toggle a product in customer's wishlist."""
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not current_user.is_authenticated:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Please log in to manage your wishlist.', 'require_login': True}), 401
        flash('Please log in to add items to your wishlist.', 'warning')
        return redirect(url_for('auth.login', next=request.referrer))

    product = Product.query.get_or_404(product_id)
    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=product.id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        added = False
        msg = f'Removed "{product.name}" from your wishlist.'
    else:
        new_item = Wishlist(user_id=current_user.id, product_id=product.id)
        db.session.add(new_item)
        db.session.commit()
        added = True
        msg = f'Added "{product.name}" to your wishlist.'

    if is_ajax:
        return jsonify({
            'success': True,
            'added': added,
            'message': msg,
            'wishlist_count': current_user.wishlist_items.count()
        })

    flash(msg, 'info')
    return redirect(request.referrer or url_for('auth.profile'))
