from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash, current_app
from app.models.product import Product

cart_bp = Blueprint('cart', __name__)


def get_cart_summary():
    """Helper to compute subtotal, items count, shipping, discount, and final total."""
    cart = session.get('cart', {})
    items = list(cart.values())
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    items_count = sum(item['quantity'] for item in items)

    free_shipping_threshold = current_app.config.get('FREE_SHIPPING_THRESHOLD', 999.0)
    standard_shipping = current_app.config.get('STANDARD_SHIPPING_FEE', 99.0)

    # Shipping fee calculation
    if subtotal == 0 or subtotal >= free_shipping_threshold:
        shipping_fee = 0.0
    else:
        shipping_fee = standard_shipping

    # Promo discount calculation
    promo = session.get('applied_promo', None)
    discount = 0.0
    if promo:
        if promo.get('type') == 'percent':
            discount = round(subtotal * (promo.get('value', 0) / 100), 2)
        elif promo.get('type') == 'flat':
            discount = min(subtotal, promo.get('value', 0))

    # Tax calculation (5% GST on art supplies after discount)
    taxable_amount = max(0.0, subtotal - discount)
    tax = round(taxable_amount * current_app.config.get('TAX_RATE', 0.05), 2)
    grand_total = round(taxable_amount + shipping_fee + tax, 2)

    # Shipping progress (percentage toward free shipping threshold)
    shipping_progress = min(100, int((subtotal / free_shipping_threshold) * 100)) if free_shipping_threshold > 0 else 100
    amount_needed_for_free_shipping = max(0.0, free_shipping_threshold - subtotal)

    return {
        'items': items,
        'cart_items': items,
        'subtotal': subtotal,
        'items_count': items_count,
        'shipping_fee': shipping_fee,
        'discount': discount,
        'tax': tax,
        'grand_total': grand_total,
        'shipping_progress': shipping_progress,
        'amount_needed_for_free_shipping': amount_needed_for_free_shipping,
        'promo': promo
    }


@cart_bp.route('/')
def view_cart():
    """Full shopping cart page with item modifications and summary."""
    summary = get_cart_summary()
    return render_template('cart/index.html', summary=summary)


@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    """Add a product to cart. Responds to both AJAX and standard form submissions."""
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.is_json:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
    else:
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', 1, type=int)

    if not product_id or quantity <= 0:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Invalid product or quantity'}), 400
        flash('Invalid product selection.', 'danger')
        return redirect(request.referrer or url_for('shop.catalog'))

    product = Product.query.get(product_id)
    if not product or not product.is_active:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Product is currently unavailable'}), 404
        flash('Product is currently unavailable.', 'danger')
        return redirect(request.referrer or url_for('shop.catalog'))

    # Retrieve or initialize cart dictionary
    cart = session.get('cart', {})
    prod_key = str(product.id)

    current_qty = cart[prod_key]['quantity'] if prod_key in cart else 0
    new_qty = current_qty + quantity

    # Check stock
    if new_qty > product.stock_quantity:
        new_qty = product.stock_quantity
        message = f"Only {product.stock_quantity} units available in stock. Quantity adjusted."
    else:
        message = f'Added "{product.name}" to your cart.'

    cart[prod_key] = {
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'compare_at_price': float(product.compare_at_price) if product.compare_at_price else None,
        'image_url': product.primary_image_url,
        'slug': product.slug,
        'category_name': product.category.name if product.category else 'Art Supplies',
        'quantity': new_qty,
        'stock': product.stock_quantity
    }

    session['cart'] = cart
    session.modified = True

    if is_ajax:
        summary = get_cart_summary()
        return jsonify({
            'success': True,
            'message': message,
            'cart_count': summary['items_count'],
            'cart_subtotal': summary['subtotal'],
            'cart_items': summary['items']
        })

    flash(message, 'success')
    return redirect(request.referrer or url_for('cart.view_cart'))


@cart_bp.route('/update', methods=['POST'])
def update_cart():
    """Update item quantities."""
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.is_json:
        data = request.get_json()
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
    else:
        product_id = str(request.form.get('product_id'))
        quantity = request.form.get('quantity', 1, type=int)

    cart = session.get('cart', {})

    if product_id in cart:
        if quantity <= 0:
            del cart[product_id]
            msg = 'Item removed from cart.'
        else:
            product = Product.query.get(int(product_id))
            max_stock = product.stock_quantity if product else 99
            cart[product_id]['quantity'] = min(quantity, max_stock)
            msg = 'Cart updated successfully.'

        session['cart'] = cart
        session.modified = True
    else:
        msg = 'Item not found in cart.'

    if is_ajax:
        summary = get_cart_summary()
        return jsonify({
            'success': True,
            'message': msg,
            'summary': summary
        })

    flash(msg, 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove/<int:product_id>', methods=['GET', 'POST'])
def remove_from_cart(product_id):
    """Remove item from cart."""
    cart = session.get('cart', {})
    prod_key = str(product_id)

    if prod_key in cart:
        item_name = cart[prod_key]['name']
        del cart[prod_key]
        session['cart'] = cart
        session.modified = True
        flash(f'Removed "{item_name}" from cart.', 'info')

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        summary = get_cart_summary()
        return jsonify({
            'success': True,
            'message': 'Item removed',
            'summary': summary
        })

    return redirect(request.referrer or url_for('cart.view_cart'))


@cart_bp.route('/clear')
def clear_cart():
    """Empty the shopping cart."""
    session.pop('cart', None)
    session.pop('applied_promo', None)
    session.modified = True
    flash('Your cart has been cleared.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/apply-promo', methods=['POST'])
def apply_promo():
    """Apply discount voucher code."""
    promo_code = request.form.get('promo_code', '').strip().upper()

    valid_promos = {
        'CREATE10': {'type': 'percent', 'value': 10, 'label': '10% Welcome Artist Discount'},
        'ARTORA50': {'type': 'flat', 'value': 50, 'label': '₹50 Studio Voucher'},
        'MASTERPIECE': {'type': 'percent', 'value': 15, 'label': '15% Masterpiece Discount'}
    }

    if promo_code in valid_promos:
        session['applied_promo'] = {
            'code': promo_code,
            **valid_promos[promo_code]
        }
        session.modified = True
        flash(f'Coupon "{promo_code}" applied successfully! You saved on this order.', 'success')
    else:
        flash('Invalid promo code. Try "CREATE10" for 10% off your order.', 'warning')

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove-promo')
def remove_promo():
    """Remove active promo voucher."""
    session.pop('applied_promo', None)
    session.modified = True
    flash('Coupon removed.', 'info')
    return redirect(url_for('cart.view_cart'))
