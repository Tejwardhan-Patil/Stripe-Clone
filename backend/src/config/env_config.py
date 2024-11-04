import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class EnvConfig:
    """Class responsible for loading and managing environment variables."""

    # Application Configurations
    APP_NAME = os.getenv('APP_NAME', 'StripeClone')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')

    # Database Configurations
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'stripe_clone_db')
    DB_USER = os.getenv('DB_USER', 'db_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'db_password')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'

    # Redis Configurations
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_PORT', '6379')
    REDIS_DB = os.getenv('REDIS_DB', '0')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

    # Stripe API Configurations
    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

    # PayPal API Configurations
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
    PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', '')
    PAYPAL_ENVIRONMENT = os.getenv('PAYPAL_ENVIRONMENT', 'sandbox')

    # JWT Configurations
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '86400'))

    # Email Configurations
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.mailtrap.io')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'

    # Security Configurations
    ENABLE_CORS = os.getenv('ENABLE_CORS', 'False').lower() == 'true'
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '*')
    CORS_ALLOWED_METHODS = os.getenv('CORS_ALLOWED_METHODS', 'GET,POST,PUT,DELETE')
    CORS_ALLOWED_HEADERS = os.getenv('CORS_ALLOWED_HEADERS', 'Content-Type,Authorization')

    # Google OAuth Configurations
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', '')

    # Facebook OAuth Configurations
    FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID', '')
    FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET', '')
    FACEBOOK_REDIRECT_URI = os.getenv('FACEBOOK_REDIRECT_URI', '')

    # Logging Configurations
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Fraud Detection Configurations
    ENABLE_FRAUD_DETECTION = os.getenv('ENABLE_FRAUD_DETECTION', 'False').lower() == 'true'
    FRAUD_RULES_API_KEY = os.getenv('FRAUD_RULES_API_KEY', '')

    # PCI Compliance Configurations
    PCI_COMPLIANCE_ENABLED = os.getenv('PCI_COMPLIANCE_ENABLED', 'True').lower() == 'true'
    PCI_AUDIT_LOG_PATH = os.getenv('PCI_AUDIT_LOG_PATH', '/var/log/pci_audit.log')

    # Monitoring Configurations
    PROMETHEUS_METRICS_ENABLED = os.getenv('PROMETHEUS_METRICS_ENABLED', 'False').lower() == 'true'
    PROMETHEUS_METRICS_PORT = int(os.getenv('PROMETHEUS_METRICS_PORT', '8000'))

    # Load Balancer Configurations
    NGINX_CONFIG_PATH = os.getenv('NGINX_CONFIG_PATH', '/nginx/nginx.conf')

    @classmethod
    def is_testing(cls):
        """Return True if the application is running in testing mode."""
        return cls.TESTING

    @classmethod
    def get_database_uri(cls):
        """Construct and return the full database URI."""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def get_redis_uri(cls):
        """Construct and return the Redis URI."""
        if cls.REDIS_PASSWORD:
            return f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"

    @classmethod
    def is_debug(cls):
        """Return True if the application is running in debug mode."""
        return cls.DEBUG

    @classmethod
    def is_cors_enabled(cls):
        """Return True if CORS is enabled."""
        return cls.ENABLE_CORS

    @classmethod
    def get_cors_config(cls):
        """Return the CORS configuration."""
        return {
            'origins': cls.CORS_ALLOWED_ORIGINS.split(','),
            'methods': cls.CORS_ALLOWED_METHODS.split(','),
            'headers': cls.CORS_ALLOWED_HEADERS.split(',')
        }

    @classmethod
    def is_pci_compliance_enabled(cls):
        """Return True if PCI compliance is enabled."""
        return cls.PCI_COMPLIANCE_ENABLED

    @classmethod
    def get_stripe_config(cls):
        """Return Stripe configuration."""
        return {
            'api_key': cls.STRIPE_API_KEY,
            'webhook_secret': cls.STRIPE_WEBHOOK_SECRET
        }

    @classmethod
    def get_paypal_config(cls):
        """Return PayPal configuration."""
        return {
            'client_id': cls.PAYPAL_CLIENT_ID,
            'client_secret': cls.PAYPAL_CLIENT_SECRET,
            'environment': cls.PAYPAL_ENVIRONMENT
        }

    @classmethod
    def get_jwt_config(cls):
        """Return JWT configuration."""
        return {
            'secret_key': cls.JWT_SECRET_KEY,
            'algorithm': cls.JWT_ALGORITHM,
            'access_token_expires': cls.JWT_ACCESS_TOKEN_EXPIRES,
            'refresh_token_expires': cls.JWT_REFRESH_TOKEN_EXPIRES
        }

    @classmethod
    def get_email_config(cls):
        """Return email server configuration."""
        return {
            'host': cls.EMAIL_HOST,
            'port': cls.EMAIL_PORT,
            'user': cls.EMAIL_USER,
            'password': cls.EMAIL_PASSWORD,
            'use_tls': cls.EMAIL_USE_TLS
        }

    @classmethod
    def get_logging_config(cls):
        """Return logging configuration."""
        return {
            'level': cls.LOG_LEVEL,
            'format': cls.LOG_FORMAT
        }

    @classmethod
    def is_fraud_detection_enabled(cls):
        """Return True if fraud detection is enabled."""
        return cls.ENABLE_FRAUD_DETECTION

    @classmethod
    def is_prometheus_metrics_enabled(cls):
        """Return True if Prometheus metrics are enabled."""
        return cls.PROMETHEUS_METRICS_ENABLED