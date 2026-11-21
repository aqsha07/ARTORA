import re
from datetime import datetime
from app.extensions import db


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')


class Category(db.Model):
    """Product category model (All 11 essential art categories)."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    tagline = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    icon_class = db.Column(db.String(50), default='fa-palette')
    display_order = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug and self.name:
            self.slug = slugify(self.name)

    @property
    def product_count(self):
        return self.products.filter_by(is_active=True).count()

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """Artwork and art supplies product model."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    sku = db.Column(db.String(50), unique=True, nullable=True)
    brand = db.Column(db.String(100), default='ARTORA Studio')
    short_description = db.Column(db.String(350), nullable=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    compare_at_price = db.Column(db.Float, nullable=True)  # Original higher price for sale calculation
    stock_quantity = db.Column(db.Integer, default=50)
    badge = db.Column(db.String(50), nullable=True)  # 'Bestseller', 'Artisan Choice', 'New Arrival', etc.
    rating = db.Column(db.Float, default=4.8)
    reviews_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_bestseller = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    specifications = db.Column(db.Text, nullable=True)  # JSON-formatted or key:value lines
    tags = db.Column(db.String(255), nullable=True)  # comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan', order_by='ProductImage.is_primary.desc()')
    reviews = db.relationship('Review', backref='product', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug and self.name:
            self.slug = slugify(self.name)

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    @property
    def discount_percent(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            diff = self.compare_at_price - self.price
            return int(round((diff / self.compare_at_price) * 100))
        return 0

    @property
    def primary_image_url(self):
        primary = self.images.filter_by(is_primary=True).first()
        if primary:
            return primary.image_url
        first = self.images.first()
        if first:
            return first.image_url
        return 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80'

    @property
    def specs_dict(self):
        """Parse specifications lines into a dict."""
        if not self.specifications:
            return {}
        result = {}
        for line in self.specifications.split('\n'):
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                result[key.strip()] = val.strip()
        return result

    def update_rating(self):
        """Recalculate rating from reviews."""
        revs = self.reviews.all()
        if revs:
            self.rating = round(sum(r.rating for r in revs) / len(revs), 1)
            self.reviews_count = len(revs)
        else:
            self.rating = 5.0
            self.reviews_count = 0

    def __repr__(self):
        return f'<Product {self.name} - ₹{self.price}>'


class ProductImage(db.Model):
    """Product gallery image."""
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(255), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<ProductImage {self.id} for Product {self.product_id}>'


class Review(db.Model):
    """Customer product reviews."""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False, default=5)
    reviewer_name = db.Column(db.String(100), nullable=False)
    reviewer_title = db.Column(db.String(150), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    verified_buyer = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} ({self.rating}/5) for {self.product_id}>'


class Wishlist(db.Model):
    """User wishlist items."""
    __tablename__ = 'wishlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    product = db.relationship('Product')

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_wishlist'),)

    def __repr__(self):
        return f'<Wishlist User {self.user_id} - Product {self.product_id}>'
