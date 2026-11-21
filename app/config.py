import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')


class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'artora-craft-without-limits-default-key-2026')
    
    # Database configuration
    # Default uses SQLite locally if MySQL isn't configured, but supports full MySQL connection string
    db_url = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'artora.db'}")
    if db_url.startswith('mysql://'):
        db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Razorpay Test Mode configuration
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_ARTORA2026DEMO')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'artoraSecretKeyTestMode2026')
    RAZORPAY_CURRENCY = os.getenv('RAZORPAY_CURRENCY', 'INR')

    # Application settings
    SITE_NAME = 'ARTORA'
    SITE_TAGLINE = 'Create Without Limits.'
    CURRENCY_SYMBOL = '₹'
    FREE_SHIPPING_THRESHOLD = 999.00
    STANDARD_SHIPPING_FEE = 99.00
    TAX_RATE = 0.05  # 5% GST for art essentials

    # Uploads
    UPLOAD_FOLDER = BASE_DIR / 'app' / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
