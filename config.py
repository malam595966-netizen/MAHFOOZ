import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mahfooz_super_secure_key_patna_2025')
    
    # MySQL configurations
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'mahfooz_restaurant')
    
    # Priority MySQL URI
    MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    SQLITE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'mahfooz_restaurant.db')}"
    
    ALLOW_SQLITE_FALLBACK = os.environ.get('ALLOW_SQLITE_FALLBACK', 'True').lower() in ('true', '1', 't')
    
    # Try connecting to MySQL; if unavailable and fallback allowed, use SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Razorpay Payment Gateway settings
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_MahfoozDemoKey')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'MahfoozSecretKey987654321')
    RAZORPAY_CURRENCY = os.environ.get('RAZORPAY_CURRENCY', 'INR')

    # Direct UPI Payment configuration
    RESTAURANT_UPI_ID = os.environ.get('RESTAURANT_UPI_ID', 'mahfoozrestaurant@oksbi')
    RESTAURANT_UPI_NAME = os.environ.get('RESTAURANT_UPI_NAME', 'MAHFOOZ RESTAURANT PATNA')

    
    @classmethod
    def get_database_uri(cls):
        # Allow explicit override via DATABASE_URL
        custom_url = os.environ.get('DATABASE_URL')
        if custom_url:
            return custom_url

        # Check if MySQL can be reached
        try:
            import pymysql
            port = int(cls.MYSQL_PORT) if cls.MYSQL_PORT else 3306
            conn = pymysql.connect(
                host=cls.MYSQL_HOST,
                user=cls.MYSQL_USER,
                password=cls.MYSQL_PASSWORD,
                port=port,
                connect_timeout=2
            )
            # Ensure the database exists or create it
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{cls.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            conn.close()
            print(f"[DATABASE] Successfully connected to MySQL server. Using database: '{cls.MYSQL_DB}'")
            return cls.MYSQL_URI
        except Exception as e:
            if cls.ALLOW_SQLITE_FALLBACK:
                print(f"[DATABASE WARNING] MySQL not reachable ({e}). Gracefully falling back to local SQLite database.")
                return cls.SQLITE_URI
            else:
                print(f"[DATABASE NOTICE] Attempting MySQL URI directly: {cls.MYSQL_URI}")
                return cls.MYSQL_URI

SQLALCHEMY_DATABASE_URI = Config.get_database_uri()
