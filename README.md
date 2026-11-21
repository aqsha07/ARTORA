# ARTORA — Create Without Limits.

> **ARTORA** is a full-stack, fine art supplies and studio essentials e-commerce platform crafted with modern Python Flask, MySQL, Flask-Login, Razorpay test mode payment processing, and a bespoke warm-ivory / terracotta design system.

---

## 🎨 Brand Identity

- **Brand Name:** ARTORA
- **Tagline:** *Create Without Limits.*
- **Mission:** Sourcing authentic single-pigment paints, Belgian linen surfaces, organic honey watercolors, hand-cupped Kolinsky sable brushes, and artist combos for visual creators, portrait ateliers, and art academies.

---

## 📦 Product Categories (All 11 Core Departments)

1. **Canvas and Painting Surfaces** — Belgian stretched linen, cotton duck boards, birch wood cradled panels.
2. **Acrylic Paints** — Heavy body acrylics, fluid gouache, lustrous mica metallics.
3. **Oil Paints** — Florentine triple-milled single-pigment oils, cold-pressed linseed mediums, non-yellowing whites.
4. **Watercolor Paints** — Botanical wild honey-bound half-pans, sedimentary granulating mineral tubes.
5. **Paint Brushes** — Kolinsky sables, Chungking hog filberts, Japanese sheep hair hake wash brushes.
6. **Drawing and Sketching** — Archival 9B–9H graphites, willow vine charcoals, waterproof micron fineliners.
7. **Art Papers and Sketchbooks** — 100% cotton 300 GSM cold-pressed blocks, lay-flat terracotta mixed media journals.
8. **Easels and Painting Tools** — Steamed beechwood studio H-frame cranks, flexible spring-steel palette knives.
9. **DIY and Craft Supplies** — Master relief linocut printmaking sets, oven-bake polymer clays.
10. **Artist Accessories** — 7-well porcelain mixing palettes, 16oz waxed studio canvas aprons.
11. **Art Kits and Combos** — The Master Atelier Oil Chest, Botanical Watercolor Discovery Suite, Urban Sketcher Kit.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.12, Flask 3.1.3 (Modular Blueprint Architecture) |
| **Authentication** | Flask-Login with Werkzeug Password Hashing (`pbkdf2:sha256`) |
| **Database** | MySQL (via `PyMySQL` and `Flask-SQLAlchemy`), with seamless local SQLite fallback |
| **Payment Gateway**| Razorpay Test Mode (`checkout.razorpay.com/v1/checkout.js` + Python SDK) |
| **Frontend** | Semantic HTML5, Modern CSS3 (CSS Variables, Flexbox, Grid), Vanilla ES6 JavaScript |
| **Typography** | *Playfair Display* (Serif Headings) & *Plus Jakarta Sans* (Body/UI) |
| **Icons** | Font Awesome 6.5.1 |

---

## 🏛️ Project Structure

```
ARTORA/
├── app/
│   ├── __init__.py               # Application factory create_app(), context processors, filters
│   ├── config.py                 # Configuration classes (Dev, Prod, MySQL / SQLite)
│   ├── extensions.py             # SQLAlchemy and LoginManager instances
│   ├── models/                   # Modular database models
│   │   ├── __init__.py
│   │   ├── user.py               # User, Address (Customer & Admin roles)
│   │   ├── product.py            # Category, Product, ProductImage, Review, Wishlist
│   │   └── order.py              # Order, OrderItem
│   ├── routes/                   # Clean Flask blueprints
│   │   ├── __init__.py
│   │   ├── main.py               # Home, About, Contact, FAQ, Shipping
│   │   ├── shop.py               # Catalog with multi-faceted filtering, Category view, Product details
│   │   ├── cart.py               # Session cart, AJAX additions, Quantity updater, Promo codes
│   │   ├── checkout.py           # Razorpay order generation, Verification, Order finalization
│   │   ├── auth.py               # Login, Register, Profile, Order history, Wishlist
│   │   ├── admin.py              # Curator Admin Dashboard, Product CRUD, Categories, Orders
│   │   └── api.py                # Live search autocomplete, Quick view modal endpoint, Cart sync
│   ├── static/
│   │   ├── css/
│   │   │   ├── variables.css     # Design tokens (warm ivory, terracotta, sage green, charcoal)
│   │   │   ├── base.css          # Reset, navbar, announcement bar, footer, buttons, alerts
│   │   │   ├── components.css    # Rounded product cards, mini-cart drawer, quick view modal
│   │   │   ├── shop.css          # Catalog layout, filters, product detail gallery, specs, reviews
│   │   │   ├── cart.css          # Cart table, free shipping meter, checkout steps, invoice receipt
│   │   │   ├── auth.css          # Auth cards, profile dashboard tabs, order history cards
│   │   │   └── admin.css         # Admin metrics cards, inventory data tables, status badges
│   │   └── js/
│   │       ├── main.js           # Live search modal, drawer triggers, global AJAX cart & wishlist
│   │       ├── shop.js           # Gallery thumbnail switcher, quick-view modal handler
│   │       ├── cart.js           # Cart quantity adjustments
│   │       └── checkout.js       # Razorpay checkout handler & sandbox test simulator
│   └── templates/
│       ├── base.html             # Master layout with navbar, footer, modals, drawers
│       ├── components/           # Reusable components
│       │   ├── navbar.html       # Sticky navbar with mega category dropdown
│       │   ├── footer.html       # Brand footer, newsletter, payment badges
│       │   ├── product_card.html # Signature rounded product card component
│       │   ├── mini_cart.html    # Slide-out cart drawer with free shipping tracker
│       │   ├── quick_view_modal.html # Modal for instantaneous product preview
│       │   ├── search_modal.html # Real-time search autocomplete modal
│       │   └── pagination.html   # Reusable pagination component
│       ├── main/                 # Homepage, About, Contact, FAQs, Shipping, 404, 500
│       ├── shop/                 # Catalog, Category showcase, Product detail
│       ├── cart/                 # Full Shopping cart page
│       ├── checkout/             # Multi-step checkout & Order success receipt
│       ├── auth/                 # Login, Register, Profile dashboard, Wishlist
│       └── admin/                # Dashboard, Products management, Categories, Orders
├── seed_data.py                  # Database seeder (11 categories, 26+ products, accounts, reviews)
├── setup_mysql.sql               # MySQL creation script
├── run.py                        # Application entry point
├── requirements.txt              # Production dependencies
├── .env.example                  # Environment variable reference
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Configure Environment & Database
Copy `.env.example` to `.env`:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=artora-super-secret-craft-key-2026-unlimited

# By default, runs seamlessly on SQLite (artora.db):
DATABASE_URL=sqlite:///artora.db

# Or switch to MySQL when your MySQL server is running:
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/artora_db

RAZORPAY_KEY_ID=rzp_test_ARTORA2026DEMO
RAZORPAY_KEY_SECRET=artoraSecretKeyTestMode2026
```

### 3. Seed Database
Run the automated seeder to populate all 11 categories, 26+ curated products with high-resolution imagery, test reviews, and default accounts:
```bash
python seed_data.py
```

### 4. Start the Application
```bash
python run.py
```
Open your browser at: **`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Accounts

| Role | Email | Password | Access |
|---|---|---|---|
| **Curator Admin** | `admin@artora.com` | `ArtoraAdmin2026!` | Full Admin Panel, Product CRUD, Categories, Orders |
| **Studio Artist** | `artist@artora.com` | `ArtoraArtist2026!` | Customer Profile, Order History, Wishlist |

*(Note: The login page includes a convenient **One-Click Demo Credentials** box to auto-fill these credentials).*

---

## 💳 Razorpay Test Mode & Checkout Features

- Live Razorpay Checkout popup using test keys (`rzp_test_...`).
- Automatic fallback test sandbox simulation modal for instant testing in offline or network-isolated test environments.
- Support for Cash on Delivery (COD) and Instant Sandbox Mock Checkout.
- Real-time cart calculations with 5% GST and Free Express Shipping on orders over **₹999.00**.
- Working promo code voucher: **`CREATE10`** (10% discount) or **`ARTORA50`** (₹50 discount).

---

## 🎨 Design System Highlights

- **Warm Ivory Backgrounds:** `#FAF7F2`, `#F4EFE6`, `#FFFFFF`
- **Terracotta Accents:** `#C86D51`, `#B2583D`, `#FAF0EC`
- **Sage Green Highlights:** `#7A8F78`, `#5F735D`, `#EFF4EE`
- **Charcoal Typography:** `#1C201E`, `#2D3330`, `#6D7671`
- **Rounded Product Cards:** `border-radius: 16px`, soft shadow elevation, aspect ratio gallery thumbnails, hover zoom, and quick action icons.
- **Micro-Interactions:** Smooth slide-out cart drawer, animated free shipping progress bar, live search modal with instant debounced results, toast notifications.
- **Fully Responsive:** Tested across mobile (< 768px), tablet (768px – 1024px), and desktop (> 1024px).
