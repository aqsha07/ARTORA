import random
import string
from datetime import datetime
from app.extensions import db


def generate_order_number():
    """Generate a unique human-friendly order number."""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ART-{datetime.utcnow().strftime('%y%m')}-{suffix}"


class Order(db.Model):
    """Customer order model."""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, default=generate_order_number, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Customer & Shipping details
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=False)
    shipping_pincode = db.Column(db.String(20), nullable=False)
    order_notes = db.Column(db.Text, nullable=True)

    # Financial totals
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    shipping_fee = db.Column(db.Float, nullable=False, default=0.0)
    tax_amount = db.Column(db.Float, nullable=False, default=0.0)
    discount_amount = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)

    # Payment details
    payment_method = db.Column(db.String(50), default='razorpay')  # 'razorpay', 'cod', 'test_mode'
    payment_status = db.Column(db.String(50), default='Pending')  # 'Pending', 'Paid', 'Failed', 'Refunded'
    razorpay_order_id = db.Column(db.String(100), nullable=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    razorpay_signature = db.Column(db.String(255), nullable=True)

    # Order processing status
    status = db.Column(db.String(50), default='Processing')  # 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'
    tracking_number = db.Column(db.String(100), nullable=True)
    courier_name = db.Column(db.String(100), default='Artora Express Courier')

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def status_badge_class(self):
        mapping = {
            'Pending': 'badge-warning',
            'Processing': 'badge-primary',
            'Shipped': 'badge-info',
            'Delivered': 'badge-success',
            'Cancelled': 'badge-danger'
        }
        return mapping.get(self.status, 'badge-secondary')

    def __repr__(self):
        return f'<Order {self.order_number} - ₹{self.total_amount}>'


class OrderItem(db.Model):
    """Line item in an order."""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)

    # Snapshot of product information at time of purchase
    product_name = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Float, nullable=False)
    product_image = db.Column(db.String(500), nullable=True)

    # Relationship to live product (optional if deleted)
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem {self.product_name} x {self.quantity}>'
