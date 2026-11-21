"""
ARTORA Comprehensive Audit & Verification Script
Exhaustively tests file structure, database integrity, route connectivity,
interactive features, checkout/Razorpay simulation, and admin access control.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from app.extensions import db
from app.models.user import User, Address
from app.models.product import Category, Product, ProductImage, Review, Wishlist
from app.models.order import Order, OrderItem

REQUIRED_FILES = [
    # Core app files
    "app/__init__.py",
    "app/config.py",
    "app/extensions.py",
    
    # Models
    "app/models/__init__.py",
    "app/models/user.py",
    "app/models/product.py",
    "app/models/order.py",
    
    # Routes
    "app/routes/__init__.py",
    "app/routes/main.py",
    "app/routes/shop.py",
    "app/routes/cart.py",
    "app/routes/checkout.py",
    "app/routes/auth.py",
    "app/routes/admin.py",
    "app/routes/api.py",
    
    # CSS
    "app/static/css/variables.css",
    "app/static/css/base.css",
    "app/static/css/components.css",
    "app/static/css/shop.css",
    "app/static/css/cart.css",
    "app/static/css/auth.css",
    "app/static/css/admin.css",
    
    # JS
    "app/static/js/main.js",
    "app/static/js/shop.js",
    "app/static/js/cart.js",
    "app/static/js/checkout.js",
    
    # Templates: Components & Layout
    "app/templates/base.html",
    "app/templates/components/navbar.html",
    "app/templates/components/footer.html",
    "app/templates/components/product_card.html",
    "app/templates/components/mini_cart.html",
    "app/templates/components/quick_view_modal.html",
    "app/templates/components/search_modal.html",
    "app/templates/components/pagination.html",
    
    # Templates: Main
    "app/templates/main/index.html",
    "app/templates/main/about.html",
    "app/templates/main/contact.html",
    "app/templates/main/faq.html",
    "app/templates/main/shipping.html",
    "app/templates/main/404.html",
    "app/templates/main/500.html",
    
    # Templates: Shop
    "app/templates/shop/catalog.html",
    "app/templates/shop/category.html",
    "app/templates/shop/detail.html",
    
    # Templates: Cart & Checkout
    "app/templates/cart/index.html",
    "app/templates/checkout/checkout.html",
    "app/templates/checkout/success.html",
    
    # Templates: Auth
    "app/templates/auth/login.html",
    "app/templates/auth/register.html",
    "app/templates/auth/profile.html",
    "app/templates/auth/wishlist.html",
    
    # Templates: Admin
    "app/templates/admin/layout.html",
    "app/templates/admin/dashboard.html",
    "app/templates/admin/products.html",
    "app/templates/admin/product_form.html",
    "app/templates/admin/categories.html",
    "app/templates/admin/orders.html",
    "app/templates/admin/order_detail.html",
    
    # Project Root
    "run.py",
    "seed_data.py",
    "setup_mysql.sql",
    "requirements.txt",
    ".env",
    ".env.example",
    "README.md"
]

EXPECTED_CATEGORIES = [
    "Canvas and Painting Surfaces",
    "Acrylic Paints",
    "Oil Paints",
    "Watercolor Paints",
    "Paint Brushes",
    "Drawing and Sketching",
    "Art Papers and Sketchbooks",
    "Easels and Painting Tools",
    "DIY and Craft Supplies",
    "Artist Accessories",
    "Art Kits and Combos"
]


def audit_files():
    print("\n--- 1. FILE EXISTENCE & INTEGRITY CHECK ---")
    missing = []
    for file_path in REQUIRED_FILES:
        full = BASE_DIR / file_path
        if not full.exists():
            missing.append(file_path)
            print(f"  [MISSING] {file_path}")
        else:
            size = full.stat().st_size
            if size == 0:
                missing.append(f"{file_path} (Empty file)")
                print(f"  [EMPTY]   {file_path}")
            else:
                pass
    if missing:
        print(f"FAILED: {len(missing)} files missing or empty!")
        return False
    print(f"PASSED: All {len(REQUIRED_FILES)} required files exist and contain content.")
    return True


def audit_database(app):
    print("\n--- 2. DATABASE CONFIGURATION & DATA INTEGRITY CHECK ---")
    with app.app_context():
        # Check tables
        tables = db.metadata.tables.keys()
        print(f"  Detected tables in metadata: {', '.join(tables)}")
        
        # Check categories
        cats = Category.query.all()
        cat_names = [c.name for c in cats]
        print(f"  Categories in database ({len(cats)}):")
        for name in EXPECTED_CATEGORIES:
            if name in cat_names:
                print(f"    ✓ {name}")
            else:
                print(f"    ✗ MISSING: {name}")
                return False

        # Check products
        products = Product.query.all()
        print(f"  Total products in database: {len(products)}")
        assert len(products) >= 20, f"Expected at least 20 products, got {len(products)}"
        
        # Check users
        admin = User.query.filter_by(role='admin').first()
        customer = User.query.filter_by(role='user').first()
        assert admin is not None, "Admin user not found"
        assert customer is not None, "Customer user not found"
        print(f"  Found Admin: {admin.email}")
        print(f"  Found Customer: {customer.email}")

    print("PASSED: Database tables, models, and seeded records are healthy.")
    return True


def audit_routes_and_pages(client):
    print("\n--- 3. FRONTEND PAGES & ROUTE CONNECTIVITY CHECK ---")
    get_routes = [
        ('/', "Homepage"),
        ('/about', "About Page"),
        ('/contact', "Contact Page"),
        ('/faq', "FAQ Page"),
        ('/shipping', "Shipping Page"),
        ('/shop/', "Shop Catalog"),
        ('/shop/bestsellers', "Bestsellers Redirect/Page"),
        ('/shop/combos', "Combos Redirect/Page"),
        ('/cart/', "Cart Page"),
        ('/auth/login', "Login Page"),
        ('/auth/register', "Register Page"),
        ('/non-existent-page-xyz', "404 Error Handler")
    ]

    for route, label in get_routes:
        res = client.get(route, follow_redirects=True)
        expected_status = 404 if '404' in label else 200
        assert res.status_code == expected_status, f"{label} ({route}) returned {res.status_code}, expected {expected_status}"
        print(f"  ✓ {label} ({route}) -> HTTP {res.status_code}")

    # Check all category pages
    cats = Category.query.all()
    for cat in cats:
        res = client.get(f'/shop/category/{cat.slug}')
        assert res.status_code == 200, f"Category page {cat.slug} returned {res.status_code}"
        assert cat.name.encode('utf-8') in res.data
    print(f"  ✓ All {len(cats)} individual Category showcase pages render HTTP 200")

    # Check sample product detail pages
    prods = Product.query.limit(5).all()
    for prod in prods:
        res = client.get(f'/shop/product/{prod.slug}')
        assert res.status_code == 200, f"Product detail {prod.slug} returned {res.status_code}"
        assert prod.name.encode('utf-8') in res.data or b"product-detail-title" in res.data
    print(f"  ✓ Product detail pages render HTTP 200")

    print("PASSED: All frontend pages connect to Flask routes without template errors.")
    return True


def audit_interactive_features(client):
    print("\n--- 4. INTERACTIVE FEATURES & API TESTING ---")
    
    # 1. Live search API
    res = client.get('/api/live-search?q=linen')
    assert res.status_code == 200
    data = res.get_json()
    assert 'products' in data and 'categories' in data
    print(f"  ✓ Live Search Autocomplete API returned {len(data['products'])} products")

    # 2. Quick view modal API
    prod = Product.query.first()
    res = client.get(f'/api/product/{prod.id}/quick-view')
    assert res.status_code == 200
    qv_data = res.get_json()
    assert qv_data['name'] == prod.name
    print(f"  ✓ Quick View Modal API returned product: {qv_data['name']}")

    # 3. Add to cart via AJAX JSON
    res = client.post('/cart/add', json={'product_id': prod.id, 'quantity': 1})
    assert res.status_code == 200
    cart_res = res.get_json()
    assert cart_res['success'] is True
    print(f"  ✓ AJAX Add-to-Cart OK (Cart count: {cart_res['cart_count']})")

    # 4. Cart Summary API
    res = client.get('/api/cart/summary')
    assert res.status_code == 200
    summary = res.get_json()
    assert summary['items_count'] >= 1
    assert summary['subtotal'] > 0
    print(f"  ✓ Cart Summary API OK (Subtotal: ₹{summary['subtotal']})")

    # 5. Promo Code Application
    res = client.post('/cart/apply-promo', data={'promo_code': 'CREATE10'}, follow_redirects=True)
    assert res.status_code == 200
    res = client.get('/api/cart/summary')
    summary_with_promo = res.get_json()
    assert summary_with_promo['discount'] > 0
    print(f"  ✓ Promo Code 'CREATE10' verified (Discount: ₹{summary_with_promo['discount']})")

    # 6. User Login & Profile
    res = client.post('/auth/login', data={'email': 'artist@artora.com', 'password': 'ArtoraArtist2026!'}, follow_redirects=True)
    assert res.status_code == 200
    res = client.get('/auth/profile')
    assert res.status_code == 200
    assert b"Mira Kapoor" in res.data
    print("  ✓ Customer Authentication & Profile Dashboard OK")

    # 7. Wishlist Toggle API
    res = client.post(f'/auth/wishlist/toggle/{prod.id}', headers={'X-Requested-With': 'XMLHttpRequest'})
    assert res.status_code == 200
    wishlist_res = res.get_json()
    assert wishlist_res['success'] is True
    print(f"  ✓ Wishlist Toggle OK (Added: {wishlist_res['added']})")

    # 8. Razorpay Order Creation Endpoint
    res = client.post('/checkout/create-razorpay-order')
    assert res.status_code == 200
    rzp = res.get_json()
    assert rzp['success'] is True
    assert 'razorpay_order_id' in rzp
    print(f"  ✓ Razorpay Order Creation OK: {rzp['razorpay_order_id']}")

    # 9. Complete Checkout Order Processing
    initial_stock = prod.stock_quantity
    res = client.post('/checkout/process-order', data={
        'full_name': 'Mira Kapoor',
        'email': 'artist@artora.com',
        'phone': '+91 9876543210',
        'street_address': 'Flat 402, Lotus Studios',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'pincode': '560038',
        'order_notes': 'Please deliver carefully',
        'payment_method': 'razorpay',
        'razorpay_payment_id': 'pay_test_audit123',
        'razorpay_order_id': rzp['razorpay_order_id'],
        'razorpay_signature': 'audit_test_sig'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Your Creation Journey Begins" in res.data or b"Order Confirmed" in res.data

    # Check order was saved in database
    latest_order = Order.query.order_by(Order.id.desc()).first()
    assert latest_order is not None
    assert latest_order.email == 'artist@artora.com'
    print(f"  ✓ Order Processed & Persisted: {latest_order.order_number} (Status: {latest_order.status})")

    # Check inventory deduction
    prod_updated = Product.query.get(prod.id)
    assert prod_updated.stock_quantity == initial_stock - 1
    print(f"  ✓ Stock inventory properly decremented from {initial_stock} to {prod_updated.stock_quantity}")

    # 10. Admin Access Control & CRUD
    # First, test that regular user cannot access admin
    res = client.get('/admin/', follow_redirects=True)
    assert b"Admin authorization required" in res.data or res.status_code in (302, 403)
    print("  ✓ Non-admin access to Curator Panel correctly blocked")

    # Login as admin
    client.get('/auth/logout', follow_redirects=True)
    res = client.post('/auth/login', data={'email': 'admin@artora.com', 'password': 'ArtoraAdmin2026!'}, follow_redirects=True)
    assert res.status_code == 200

    # Access admin dashboard
    res = client.get('/admin/')
    assert res.status_code == 200
    assert b"Atelier Overview" in res.data
    print("  ✓ Admin authenticated successfully into Curator Panel")

    # Admin: Create New Product
    new_prod_data = {
        'name': 'Audit Test Sable Brush #4',
        'category_id': Category.query.first().id,
        'brand': 'ARTORA Atelier',
        'price': '850.00',
        'compare_at_price': '999.00',
        'stock_quantity': '30',
        'badge': 'New Arrival',
        'image_url': 'https://images.unsplash.com/photo-1525909002-1b05e0c869d8?auto=format&fit=crop&w=400&q=80',
        'short_description': 'Test short description',
        'description': 'Full test description for audit verification.',
        'specifications': 'Hair: Kolinsky\nSize: #4',
        'is_featured': 'y',
        'is_active': 'y'
    }
    res = client.post('/admin/products/new', data=new_prod_data, follow_redirects=True)
    assert res.status_code == 200
    created_prod = Product.query.filter_by(name='Audit Test Sable Brush #4').first()
    assert created_prod is not None
    print(f"  ✓ Admin Product Creation OK: {created_prod.name} (ID: {created_prod.id})")

    # Admin: Update Order Status
    res = client.post(f'/admin/orders/{latest_order.id}', data={
        'status': 'Shipped',
        'courier_name': 'Blue Dart Express',
        'tracking_number': 'BDT-88997766'
    }, follow_redirects=True)
    assert res.status_code == 200
    latest_order_updated = Order.query.get(latest_order.id)
    assert latest_order_updated.status == 'Shipped'
    assert latest_order_updated.tracking_number == 'BDT-88997766'
    print(f"  ✓ Admin Order Status Update OK (New status: {latest_order_updated.status}, Tracking: {latest_order_updated.tracking_number})")

    # Clean up test product
    db.session.delete(created_prod)
    db.session.commit()
    print("  ✓ Admin Product Cleanup OK")

    print("PASSED: All interactive features, Razorpay simulation, and admin workflows operate flawlessly.")
    return True


def run_full_audit():
    print("==================================================================")
    print("      ARTORA E-COMMERCE FULL SYSTEM AUDIT & VERIFICATION          ")
    print("==================================================================")

    f_ok = audit_files()
    assert f_ok, "File check failed"

    app = create_app('development')
    db_ok = audit_database(app)
    assert db_ok, "Database check failed"

    with app.test_client() as client:
        r_ok = audit_routes_and_pages(client)
        assert r_ok, "Route check failed"

        i_ok = audit_interactive_features(client)
        assert i_ok, "Interactive check failed"

    print("\n==================================================================")
    print("  [SUCCESS] 100% OF CHECKS PASSED. SYSTEM IS COMPLETELY HEALTHY! ")
    print("==================================================================")


if __name__ == '__main__':
    run_full_audit()
