"""
ARTORA Verification Script
Tests routes, blueprint registration, database queries, and cart operations.
"""

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Category, Product

app = create_app('development')

def run_tests():
    with app.test_client() as client:
        print("1. Testing Homepage...")
        res = client.get('/')
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert b"ARTORA" in res.data
        assert b"Create Without Limits" in res.data
        print("   ✓ Homepage OK")

        print("2. Testing Shop Catalog...")
        res = client.get('/shop/')
        assert res.status_code == 200
        print("   ✓ Catalog OK")

        print("3. Testing All 11 Categories...")
        categories = Category.query.all()
        print(f"   Found {len(categories)} categories:")
        for cat in categories:
            res = client.get(f'/shop/category/{cat.slug}')
            assert res.status_code == 200, f"Failed for {cat.slug}: {res.status_code}"
            print(f"     ✓ {cat.name} (Slug: {cat.slug})")

        print("4. Testing Product Detail...")
        prod = Product.query.first()
        assert prod is not None, "No products found in DB"
        res = client.get(f'/shop/product/{prod.slug}')
        assert res.status_code == 200
        assert prod.name.encode('utf-8') in res.data or b"product-detail-title" in res.data
        print(f"   ✓ Product detail OK for: {prod.name}")

        print("5. Testing Cart Operations...")
        res = client.post('/cart/add', data={'product_id': prod.id, 'quantity': 2}, follow_redirects=True)
        assert res.status_code == 200
        assert b"cart-items-table" in res.data
        print("   ✓ Add to cart OK")

        print("6. Testing Live Search API...")
        res = client.get('/api/live-search?q=canvas')
        assert res.status_code == 200
        data = res.get_json()
        assert 'products' in data and 'categories' in data
        print(f"   ✓ Live search API OK (Returned {len(data['products'])} products)")

        print("7. Testing Authentication & Admin Access...")
        # Login as Admin
        res = client.post('/auth/login', data={'email': 'admin@artora.com', 'password': 'ArtoraAdmin2026!'}, follow_redirects=True)
        assert res.status_code == 200
        print("   ✓ Admin Login OK")

        # Admin Dashboard
        res = client.get('/admin/')
        assert res.status_code == 200
        assert b"Atelier Overview" in res.data
        print("   ✓ Admin Dashboard OK")

        # Admin Products
        res = client.get('/admin/products')
        assert res.status_code == 200
        print("   ✓ Admin Products List OK")

        # Admin Categories
        res = client.get('/admin/categories')
        assert res.status_code == 200
        print("   ✓ Admin Categories List OK")

        # Admin Orders
        res = client.get('/admin/orders')
        assert res.status_code == 200
        print("   ✓ Admin Orders List OK")

        print("8. Testing End-to-End Checkout Flow...")
        # Add item to cart first
        client.post('/cart/add', data={'product_id': prod.id, 'quantity': 1}, follow_redirects=True)
        
        # Test Razorpay order creation API
        res = client.post('/checkout/create-razorpay-order')
        assert res.status_code == 200
        rzp_data = res.get_json()
        assert rzp_data['success'] is True
        assert 'razorpay_order_id' in rzp_data
        print(f"   ✓ Razorpay Order Create API OK: {rzp_data['razorpay_order_id']}")

        # Submit final order (Simulated test payment)
        res = client.post('/checkout/process-order', data={
            'full_name': 'Mira Kapoor',
            'email': 'artist@artora.com',
            'phone': '+91 9876543210',
            'street_address': 'Flat 402, Lotus Art Studios, 14th Main',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560038',
            'payment_method': 'razorpay',
            'razorpay_payment_id': 'pay_test_testsuite123',
            'razorpay_order_id': rzp_data['razorpay_order_id'],
            'razorpay_signature': 'simulated_sig'
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"Order Confirmed" in res.data or b"Your Creation Journey Begins" in res.data
        print("   ✓ End-to-End Checkout & Order Confirmation OK")

    print("\n==========================================")
    print("ALL ARTORA VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==========================================")

if __name__ == '__main__':
    # Initialize DB for testing if needed
    with app.app_context():
        from seed_data import seed_database
        seed_database()
    run_tests()
