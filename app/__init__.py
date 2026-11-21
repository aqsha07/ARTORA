import os
from flask import Flask, render_template, session
from app.config import config_by_name
from app.extensions import db, login_manager


def create_app(config_name=None):
    """Application factory for ARTORA e-commerce store."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    try:
        db.init_app(app)
    except Exception as e:
        print(f"[ARTORA DB Warning] {e}. Falling back to SQLite.")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artora.db'
        db.init_app(app)

    login_manager.init_app(app)

    # User loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.shop import shop_bp
    from app.routes.cart import cart_bp
    from app.routes.checkout import checkout_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(shop_bp, url_prefix='/shop')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(checkout_bp, url_prefix='/checkout')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Global template context processors
    @app.context_processor
    def inject_global_data():
        from app.models.product import Category
        try:
            categories = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
        except Exception:
            categories = []

        # Calculate session cart items count and total
        cart = session.get('cart', {})
        total_items = sum(item.get('quantity', 1) for item in cart.values()) if isinstance(cart, dict) else 0
        cart_subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart.values()) if isinstance(cart, dict) else 0.0

        return {
            'site_name': app.config.get('SITE_NAME', 'ARTORA'),
            'site_tagline': app.config.get('SITE_TAGLINE', 'Create Without Limits.'),
            'currency_symbol': app.config.get('CURRENCY_SYMBOL', '₹'),
            'free_shipping_threshold': app.config.get('FREE_SHIPPING_THRESHOLD', 999.0),
            'header_categories': categories,
            'cart_items_count': total_items,
            'cart_subtotal': cart_subtotal,
            'razorpay_key_id': app.config.get('RAZORPAY_KEY_ID', '')
        }

    # Custom Jinja filters
    @app.template_filter('currency')
    def format_currency(value):
        try:
            val = float(value)
            # Indian numbering format / standard two decimal
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return f"₹0.00"

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('main/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('main/500.html'), 500

    # Auto-create tables if running in development
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[ARTORA DB Warning during create_all]: {e}")
            if 'mysql' in str(app.config.get('SQLALCHEMY_DATABASE_URI', '')):
                print("[ARTORA] MySQL connection failed. Reconnecting to local SQLite database...")
                app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artora.db'
                db.create_all()

    return app
