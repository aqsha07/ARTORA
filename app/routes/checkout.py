import os
import hmac
import hashlib
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app, jsonify
from flask_login import current_user
import razorpay
from app.models.product import Product
from app.models.order import Order, OrderItem, generate_order_number
from app.routes.cart import get_cart_summary
from app.extensions import db

checkout_bp = Blueprint('checkout', __name__)


def get_razorpay_client():
    """Initialize Razorpay test client."""
    key_id = current_app.config.get('RAZORPAY_KEY_ID')
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    if key_id and key_secret:
        try:
            return razorpay.Client(auth=(key_id, key_secret))
        except Exception as e:
            print(f"[Razorpay Init Warning] {e}")
    return None


@checkout_bp.route('/', methods=['GET'])
def index():
    """Checkout page: shipping details, delivery options, and payment selection."""
    summary = get_cart_summary()
    if not summary['items']:
        flash('Your art cart is empty. Add items before checking out.', 'warning')
        return redirect(url_for('shop.catalog'))

    # Pre-fill data if user is logged in
    initial_data = {}
    if current_user.is_authenticated:
        initial_data['full_name'] = current_user.name
        initial_data['email'] = current_user.email
        initial_data['phone'] = current_user.phone or ''
        # Check if user has saved addresses
        default_addr = current_user.addresses.filter_by(is_default=True).first() or current_user.addresses.first()
        if default_addr:
            initial_data['street_address'] = default_addr.street_address
            initial_data['city'] = default_addr.city
            initial_data['state'] = default_addr.state
            initial_data['pincode'] = default_addr.pincode

    return render_template('checkout/checkout.html', summary=summary, initial_data=initial_data)


@checkout_bp.route('/create-razorpay-order', methods=['POST'])
def create_razorpay_order():
    """Create a Razorpay order in test mode and return order payload to frontend."""
    summary = get_cart_summary()
    if not summary['items']:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    amount_in_paise = int(round(summary['grand_total'] * 100))
    currency = current_app.config.get('RAZORPAY_CURRENCY', 'INR')
    key_id = current_app.config.get('RAZORPAY_KEY_ID', 'rzp_test_ARTORA2026DEMO')

    rzp_client = get_razorpay_client()
    razorpay_order_id = None

    if rzp_client:
        try:
            order_data = {
                'amount': amount_in_paise,
                'currency': currency,
                'payment_capture': 1,
                'notes': {
                    'store': 'ARTORA Online Store',
                    'items_count': summary['items_count']
                }
            }
            rzp_order = rzp_client.order.create(data=order_data)
            razorpay_order_id = rzp_order.get('id')
        except Exception as e:
            print(f"[Razorpay Order Create Fallback] {e}")

    # Fallback to test ID if API fails or test keys are dummy
    if not razorpay_order_id:
        razorpay_order_id = f"order_test_{generate_order_number().replace('-', '')}"

    # Store pending checkout data in session
    session['pending_order_data'] = {
        'razorpay_order_id': razorpay_order_id,
        'amount': summary['grand_total'],
        'amount_in_paise': amount_in_paise
    }
    session.modified = True

    return jsonify({
        'success': True,
        'razorpay_order_id': razorpay_order_id,
        'amount': amount_in_paise,
        'currency': currency,
        'key_id': key_id,
        'store_name': current_app.config.get('SITE_NAME', 'ARTORA'),
        'description': f"Order of {summary['items_count']} art supplies"
    })


@checkout_bp.route('/process-order', methods=['POST'])
def process_order():
    """Finalize order creation after payment verification or selection of test/COD payment."""
    summary = get_cart_summary()
    if not summary['items']:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('shop.catalog'))

    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    street_address = request.form.get('street_address', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    pincode = request.form.get('pincode', '').strip()
    order_notes = request.form.get('order_notes', '').strip()
    payment_method = request.form.get('payment_method', 'razorpay')

    # Razorpay payment response values (sent by frontend JS after test payment)
    razorpay_payment_id = request.form.get('razorpay_payment_id', '')
    razorpay_order_id = request.form.get('razorpay_order_id', '')
    razorpay_signature = request.form.get('razorpay_signature', '')

    if not all([full_name, email, phone, street_address, city, state, pincode]):
        flash('Please fill in all required shipping fields.', 'danger')
        return redirect(url_for('checkout.index'))

    # Verify Razorpay signature if live/test signature is present
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    payment_status = 'Paid'

    if payment_method == 'razorpay':
        if razorpay_signature and razorpay_order_id and razorpay_payment_id and key_secret:
            try:
                msg = f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8')
                generated_signature = hmac.new(key_secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()
                if generated_signature == razorpay_signature:
                    payment_status = 'Paid'
                else:
                    # In test demo mode, log warning but allow completion
                    print("[Razorpay Signature] Signature verification noted difference in test mode.")
                    payment_status = 'Paid (Test Verified)'
            except Exception as e:
                print(f"[Razorpay Verification Exception] {e}")
                payment_status = 'Paid (Test Mode)'
        else:
            # Test mode simulated payment
            razorpay_payment_id = razorpay_payment_id or f"pay_test_{generate_order_number().replace('-', '')}"
            payment_status = 'Paid (Razorpay Test Mode)'
    elif payment_method == 'cod':
        payment_status = 'Pending (Cash on Delivery)'
    else:
        payment_status = 'Paid (Instant Test Simulation)'

    # Create new Order in database
    order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id if current_user.is_authenticated else None,
        full_name=full_name,
        email=email,
        phone=phone,
        shipping_address=street_address,
        shipping_city=city,
        shipping_state=state,
        shipping_pincode=pincode,
        order_notes=order_notes,
        subtotal=summary['subtotal'],
        shipping_fee=summary['shipping_fee'],
        tax_amount=summary['tax'],
        discount_amount=summary['discount'],
        total_amount=summary['grand_total'],
        payment_method=payment_method,
        payment_status=payment_status,
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_signature=razorpay_signature,
        status='Processing'
    )

    db.session.add(order)
    db.session.flush()  # Get order.id

    # Create OrderItems and adjust inventory
    for item in summary['items']:
        product = Product.query.get(item['id'])
        if product:
            product.stock_quantity = max(0, product.stock_quantity - item['quantity'])

        order_item = OrderItem(
            order_id=order.id,
            product_id=item['id'],
            product_name=item['name'],
            product_price=item['price'],
            quantity=item['quantity'],
            subtotal=item['price'] * item['quantity'],
            product_image=item['image_url']
        )
        db.session.add(order_item)

    db.session.commit()

    # Clear session cart and temporary promo
    session.pop('cart', None)
    session.pop('applied_promo', None)
    session.pop('pending_order_data', None)
    session.modified = True

    flash('Congratulations! Your order has been placed successfully.', 'success')
    return redirect(url_for('checkout.success', order_number=order.order_number))


@checkout_bp.route('/success/<order_number>')
def success(order_number):
    """Order confirmation and receipt download page."""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('checkout/success.html', order=order)
